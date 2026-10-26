# Hartford Internal SPA Reference Architecture: Static Content on Compute with AWS API Gateway (Pattern SPA_Internal_04 v1)

You are designing the architecture for a new internal UI application, specifically a single-page application (SPA). Your design must follow The Hartford ("HIG") Enterprise Architecture pattern below so that internal architecture reviewers will accept it. Use these components and flows unless the requirements explicitly justify a deviation. If you deviate, call it out and explain why.

## 1. Scope and audience
- Users: Hartford employees only, on the corporate network, using HIG-managed devices joined or registered to Azure AD (Microsoft Entra ID).
- Not internet-facing. Traffic must stay on the HIG network and the AWS backbone through AWS Direct Connect. Do not route traffic over the public internet.
- Hosting: AWS, in the application's line-of-business (LOB) CloudOps account. The reference diagram uses us-east-1.
- The pattern covers three things:
  1. Static content delivery: loading the SPA's HTML, JavaScript, and CSS.
  2. End-user authentication: Azure AD single sign-on through the device's Primary Refresh Token (PRT).
  3. API access and user authorization: authentication and authorization at AWS API Gateway in front of protected backend APIs.

## 2. Required components
| Component | Role in this pattern |
|---|---|
| AWS Direct Connect | Private link from the HIG on-premises network to AWS. All user traffic enters AWS this way. |
| VPC (application private subnets, multiple AZs) | Isolated network for all workloads. |
| Route 53 Private Hosted Zone | Private DNS. Alias/CNAME for the static app hostname (e.g. `app.<domain>`) and the API custom domain (e.g. `api.<domain>`). |
| ACM | TLS certificates for the ALBs and the API Gateway custom domain. TLS 1.2+ on port 443 everywhere. |
| ALB for static content | Fronts the web servers that serve the SPA's static assets. |
| AWS compute for static content: ECS Fargate (preferred) or EC2 | Web server, such as nginx, serving the built SPA bundle. Deploy across multiple AZs. |
| Private AWS API Gateway (REST) + Interface VPC Endpoint (`execute-api`) + PrivateLink | The only entry point for all API calls from the SPA. Use a custom domain name such as `api.<domain>`. |
| Lambda Authorizer (VPC-enabled) | Validates the Azure AD access token on every API request, optionally calls the app's Authorize API for fine-grained scopes, and returns an IAM policy that allows or denies the request. |
| VPC Link (v2 per the page) + internal ALB for APIs | API Gateway cannot integrate natively with ECS. Requests reach ECS, EKS, or EC2 services through a VPC Link to an internal ALB, for example with a `/api` path. |
| Application APIs on ECS Fargate / EKS / EC2 | Dynamic/backend services. Security groups allow inbound traffic only from the API Gateway path. |
| Application APIs on AWS Lambda (optional) | API Gateway invokes Lambda directly, with no VPC Link or ALB. |
| Authorize API (application-owned service) | Returns the user's application scopes and permissions for fine-grained authorization. The Lambda Authorizer calls it when needed. |
| Azure AD (Entra ID) | Enterprise identity provider. Provides SSO, MFA, and Conditional Access, and issues JWT access tokens. |
| CloudWatch | Logs and metrics. Forward logs to Splunk according to the HIG CloudWatch-to-Splunk logging design. |
| CloudTrail | Audit, security monitoring, and API activity tracking. |
| IAM | Roles and policies for API Gateway access and tag-based admin access to compute resources. |

Infrastructure as code: provision API Gateway with the Cloud Services Team's internal Terraform module (`terraform-aws-apigateway-v1`). Use internal Hartford modules, not community modules.

## 3. Request paths
There are two hostnames and two separate paths.
- Static path (`https://app.<domain>`): Browser → Direct Connect → Route 53 private DNS → static ALB → web server on ECS Fargate/EC2 → static files.
- Dynamic/API path (`https://api.<domain>`): Browser → Direct Connect → VPC interface endpoint (`execute-api`) → Private API Gateway → Lambda Authorizer → (approved request) → VPC Link → internal API ALB → API service on ECS/EKS/EC2, or Private API Gateway → Lambda API directly.

## 4. End-to-end flow (numbered as on the reference diagram)
1. The user opens the SPA URL. The request goes to the static ALB.
2. The ALB forwards to the web server on AWS compute (ECS Fargate/EC2), which returns the static SPA bundle.
3. The SPA starts an OAuth 2.0 Authorization Code flow with PKCE against Azure AD using MSAL.js (`@azure/msal-browser`).
4. Azure AD validates the device/user SSO context backed by the PRT and authenticates the user. The PRT is issued at Windows sign-in on the Azure AD-joined device.
5. Azure AD returns a JWT access token containing the user's claims.
6. The SPA attaches `Authorization: Bearer <AzureAD access token>` to every API call. Calls go to the Private API Gateway custom domain through its VPC endpoint.
7. API Gateway invokes the Lambda Authorizer.
   - 7a. The authorizer validates the JWT against Azure AD: signature from JWKS, issuer, audience, expiry, and scopes or roles.
   - 7b. If fine-grained authorization is required, the authorizer calls the application's Authorize API to get the user's scopes and permissions.
   - 7c. The authorizer returns an IAM policy, Allow or Deny, scoped to the permitted methods and resources.
8. API Gateway evaluates the IAM policy. Unauthorized requests get 401/403 back to the SPA.
9. API Gateway sends approved requests through the VPC Link to the internal ALB, which routes them to the application API. Skip this step for Lambda-hosted APIs.
10. The application API processes the request and returns the response through API Gateway to the SPA.

Express this as a sequence diagram: User, SPA Browser, ALB, Static Content on Compute, Private API Gateway, Lambda Authorizer, Azure AD, ALB, Application API.

## 5. Key decisions (mandatory unless justified)
- The static content needs no user sign-in if it contains no HIG confidential or proprietary information, per THIP guidance. If the static content includes HIG proprietary content, access to it must be authenticated and authorized through API Gateway and Azure AD.
- The SPA itself implements OAuth 2.0 + PKCE with Azure AD using MSAL.js. Do not use an implicit flow or a client secret in the browser.
- Use a Private API Gateway with a custom domain name.
- Validate the Azure AD access token on every API request through a Lambda Authorizer. Keep token validation stateless.
- Reach ECS services through VPC Link and an ALB. Lambda APIs are invoked directly.
- Deploy dynamic and backend services on an ECS cluster or other compute. Security groups accept inbound traffic only from the API Gateway path.

## 6. Security requirements
- All traffic flows over the HIG network and AWS backbone through Direct Connect, never the internet.
- Use HTTPS only, with TLS 1.2+ on port 443. Certificates come from ACM.
- Security groups open only the required ports and source subnets for the compute and the ALBs.
- The API ALB security group allows only traffic arriving through the API Gateway VPC Link.
- Control API Gateway access with IAM roles and policies and a resource policy. Restrict the private API to its VPC endpoint.
- Use the Lambda Authorizer for fine-grained authorization, and deploy it VPC-enabled.
- Control who can access and administer ECS, EKS, or EC2 resources with tag-based IAM roles and policies.
- Users must use Azure AD-joined/registered devices. Refresh the PRT according to HIG standards.
- Clarification, not stated in this exact form on the page: the browser and SPA code never see or handle the PRT. The OS and browser SSO broker use it, and MSAL obtains tokens through Azure AD. Do not design any component that reads, stores, or forwards the PRT.

## 7. Resilience and idempotency
- Retry with exponential backoff and jitter.
- Store request metadata and response status so retries can be detected and handled safely.
- Keep token validation stateless.
- Return consistent error codes and messages to consumers.

## 8. Performance
- The application team supplies instance or task sizing based on capacity and growth.
- Tune ECS task, EKS pod, or EC2 capacity from load and performance test results.
- Use current-generation instance types that fit the workload.
- Expect some extra latency from on-premises → AWS and Azure AD round trips.
- For ECS, use target-tracking auto scaling on CPU or memory.
- The page marks data volume considerations as not applicable.

## 9. High availability
- The number of Availability Zones depends on the application's HIG metal tier, as defined in HIG's AWS Cross-Region DR guidance. Deploy across multiple AZs at minimum.

## 10. Disaster recovery (choose the strategy for the metal tier)
All strategies use Route 53 failover by repointing the app CNAME/Alias to the ALB in the secondary region. DR for the API platform ("APIC" on the page) is handled by the Shared Services team and is outside this pattern.
| Strategy | Initial provisioning | Failover | Failback |
|---|---|---|---|
| Backup & Restore | Deploy in the primary region and store backups in the secondary region | Deploy compute in the secondary region with pipelines, then update Route 53 | Restore primary compute, repoint Route 53, then terminate secondary resources |
| Pilot Light (Cold Standby) | Deploy components in both regions and spin down the secondary region | Spin up the pre-deployed secondary compute, then update Route 53 | Restore primary, repoint Route 53, then spin down the secondary region |
| Pilot Light (On-Demand) | Deploy static-content compute only in the primary region | Deploy secondary compute in real time with automated pipelines, then update Route 53 | Restore primary, repoint Route 53, then terminate secondary resources |
| Warm Standby | Deploy and run components in both regions, ready to receive traffic | Scale up secondary compute, then update Route 53 | Restore primary, repoint Route 53, then scale down the secondary region |

## 11. Operational standards to reference
- HIG/ECO AWS resource naming convention
- Mandatory cloud tagging standards
- CloudWatch Logs → Splunk logging design
- HIG AWS account structure / landing zone target state
- Private Hosted Zone DNS resolution design for internal applications
- EdgeMod traffic flow, covering on-premises ↔ AWS routing through the LOB account

## 12. Known gaps or ambiguities in the source pattern — do not assume; flag them or ask
1. Static content path: the diagram and numbered flow send static traffic directly to the ALB. One decision bullet says static assets are delivered through API Gateway HTTP proxy integration. Use the direct-ALB path as the default. Use the API Gateway path only when the static content is HIG proprietary and must be authenticated. State which path you chose and why.
2. VPC Link details: "VPC Link2" (v2) is normally an HTTP API feature, while REST private APIs use VPC Link v1 with an NLB, or with an ALB on newer AWS support. Confirm the API Gateway type and VPC Link version against the internal Terraform module, then specify the exact ALB/NLB and security-group wiring.
3. DR: the page provides no numeric RTO or RPO. Get them from the application's metal tier. API Gateway, custom domain, Lambda Authorizer, and Authorize API recovery are not described. Include them explicitly in your DR design.
4. The identity diagram also shows on-premises ADFS. Confirm whether the target state is Azure AD only.

## 13. Expected design output
- Context diagram plus the AWS component diagram: Direct Connect, VPC, AZs, subnets, ALBs, compute, API Gateway, VPC endpoint, Lambda Authorizer, Route 53, ACM, CloudWatch, CloudTrail, and IAM.
- Sequence diagram for the authentication and API authorization flow, following section 4.
- Security controls mapped to section 6.
- HA and DR choices tied to the metal tier and section 10.
- Terraform module plan using internal Hartford modules.
- List of open questions and assumptions, including the items in section 12.