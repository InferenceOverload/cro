#!/usr/bin/env python3
"""CRO v0.7: Apigee as external front door; two GCP invocation options (direct vs Cloud Run front); AD-group-only authorization."""
import os, sys
sys.path.insert(0, os.environ.get('ARCHDIAGRAM_SCRIPTS', '/mnt/skills/plugins/cloud-architecture-diagrams/scripts'))
from archdiagram import Diagram, CUSTOM

W = 'stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"'
CUSTOM['entra'] = ('<rect x="0" y="0" width="48" height="48" rx="6" fill="#0078D4"/>'
                   f'<path d="M24,9 L36,14 V24 C36,32 30,37 24,40 C18,37 12,32 12,24 V14 Z" {W}/>'
                   f'<path d="M19,24 L23,28 L30,20" {W}/>')
CUSTOM['adgroup'] = ('<rect x="0" y="0" width="48" height="48" rx="6" fill="#0078D4"/>'
                     '<circle cx="18" cy="18" r="5" fill="#fff"/><circle cx="31" cy="18" r="5" fill="#fff"/>'
                     '<path d="M8,37 C8,28 13,26 18,26 C23,26 28,28 28,37 Z M21,37 C21,30 26,27 31,27 C36,27 41,30 41,37 Z" fill="#fff"/>')

CUSTOM['apigee'] = ('<rect x="0" y="0" width="48" height="48" rx="6" fill="#4285F4"/>'
                    f'<circle cx="24" cy="22" r="9" {W}/><path d="M24,13 V31 M15,22 H33 M18,16 Q24,22 30,28 M30,16 Q24,22 18,28" {W}/>'
                    '<text x="24" y="44" text-anchor="middle" font-size="7.5" font-family="Arial" font-weight="bold" fill="#fff">APIGEE</text>')

SUB = 'The Hartford EDS Claims  |  Draft for architecture review  |  v0.7 (pattern SPA_Internal_04)  |  2026-11-06'
d = Diagram(subtitle=SUB)
TEAL = '#0B7A75'
NAVY = '#1F4E79'

NOTES = [('h', 'REQUEST PATH'),
         '1   Handler opens app.<domain> over Direct Connect',
         '2   Private API Gateway serves the SPA bundle from S3',
         '3   MSAL.js: OAuth 2.0 + PKCE; Azure AD SSO (device PRT)',
         '4   Every API call carries the Azure AD access token',
         '5   Lambda Authorizer: JWT (JWKS, iss, aud, exp) +',
         '     AD group CRO-Handlers; returns IAM policy',
         '6   API Lambda: flag = Y, age >= 30 days, version, lock',
         '7   Unchanged: return stored summary. Changed: enqueue',
         '8   Worker: snapshot to S3; WIF token; option A direct to',
         '     Agent Engine, or option B via Cloud Run front',
         '9   Agent calls Gemini; trace logged',
         '10  Summary vN stored (append-only); lock released',
         ('h', 'INGEST PATH'),
         'A   Stream captures changes to the claim data product',
         'B   Task runs only when stream has data; unloads to S3',
         'C   S3 event to SQS; Ingest Lambda processes the batch',
         'D   Upserts current claim items; data version + 1',
         'E   Summaries to Snowflake through Snowpipe (reporting)',
         ('h', 'SECURITY BASELINE'),
         'HIG pattern SPA_Internal_04 (pages 5 and 7); DR page 6',
         'Authorization = AD group membership; no claim-level',
         'restriction by design (page 3)',
         'No internet path; private DNS; TLS 1.2+; KMS; CloudTrail;',
         'CloudWatch logs to Splunk',
         'External consumers via Apigee: API key + mTLS, read-only']

# =====================================================================
# Page 1: conceptual
# =====================================================================
p = d.page('1 - Conceptual', 'CRO: On-Demand Claim Summary - Solution Architecture', 1700, 1100, 'conceptual')
p.panel('net', 30, 110, 400, 250, 'HIG network and CIO services', 'neutral')
p.panel('idp', 30, 380, 400, 120, 'Microsoft Entra ID (Azure AD)', 'azure')
p.panel('snow', 30, 700, 400, 370, 'Snowflake', 'snow')
p.panel('aws', 460, 110, 820, 960, 'AWS (LOB CloudOps account, us-east-1)', 'aws')
p.panel('gcp', 1310, 110, 360, 480, 'GCP (all AI workload): options A / B', 'gcp')

p.box('dx', 60, 160, 340, 45, 'AWS Direct Connect', ['Private path to AWS; no internet routing'], 'ext', 'net')
p.box('hd', 60, 215, 340, 50, 'Claim handler', ['HIG-joined device; MSAL.js runs in the browser'], 'ext', 'net')
p.box('cih', 60, 280, 165, 65, 'Claims Insights Hub', ['CIO-owned; future host', 'of summaries'], 'ext', 'net')
p.box('med', 235, 280, 165, 65, 'Mediation layer', ['CIO AWS service;', 'Apigee consumer'], 'ext', 'net')
p.box('sso', 60, 420, 340, 70, 'Azure AD SSO (OAuth 2.0 + PKCE)', ['Device PRT, MFA, Conditional Access;', 'token carries AD group CRO-Handlers'], 'security', 'idp')

p.box('s3ui', 485, 160, 140, 60, 'S3: UI bundle', ['Static SPA assets;', 'no proprietary content'], 'storage', 'aws')
p.box('apic', 485, 370, 140, 60, 'Apigee', ['CRO summary product;', 'API key + mTLS'], 'integ', 'aws')
p.box('r53', 645, 160, 140, 60, 'Route 53 (private)', ['app./api.<domain>', 'private hosted zone'], 'mgmt', 'aws')
p.box('ps', 805, 160, 140, 60, 'Parameter Store', ['Thresholds, e.g.', 'min claim age = 30'], 'mgmt', 'aws')
p.box('acm', 965, 160, 140, 60, 'ACM certificates', ['TLS 1.2+ on 443'], 'security', 'aws')
p.box('ct', 1125, 160, 140, 60, 'CloudTrail', ['API activity audit'], 'security', 'aws')

p.box('gw', 485, 270, 140, 80, 'Private API Gateway', ['VPC endpoint, custom', 'domain, resource policy;', '/app proxied to S3'], 'integ', 'aws')
p.box('authz', 645, 270, 140, 80, 'Lambda Authorizer', ['Stateless JWT check via', 'Azure AD JWKS; requires', 'AD group CRO-Handlers'], 'security', 'aws')
p.box('al', 805, 270, 140, 80, 'API Lambda', ['Runs only on Allow;', 'eligibility, 30-day', 'rule, version, lock'], 'compute', 'aws')
p.box('gq', 965, 270, 140, 80, 'SQS: generation', ['Buffers jobs; caps', 'concurrency and cost'], 'integ', 'aws')
p.box('wk', 1125, 270, 140, 80, 'Worker Lambda', ['Snapshot, invoke agent,', 'store summary'], 'compute', 'aws')
p.box('gd', 980, 400, 140, 44, 'DLQ: generation', [], 'integ', 'aws')
p.box('cw', 485, 440, 140, 70, 'CloudWatch', ['Logs, metrics, alarms;', 'forwarded to Splunk'], 'mgmt', 'aws')
p.box('kms', 485, 540, 140, 60, 'KMS', ['Customer-managed keys', 'for S3 and DynamoDB'], 'security', 'aws')
p.box('db', 645, 440, 300, 200, 'DynamoDB: CRO state',
      ['Current claim item (1 per claim): payload or S3', 'pointer, eligibility, open date, data version', '',
       'Summary items (append-only): text, source version,', 'prompt + model version, trace ID, snapshot ref', '',
       'In-flight lock (conditional write)'], 'db', 'aws')
p.box('s3', 1100, 560, 160, 70, 'S3: snapshots', ['Immutable model input', 'per summary + summaries'], 'storage', 'aws')
p.box('sl', 485, 925, 140, 70, 'S3: landing', ['Change files unloaded', 'from Snowflake'], 'storage', 'aws')
p.box('iq', 660, 925, 150, 70, 'SQS: ingest', ['S3 event notifications'], 'integ', 'aws')
p.box('il', 850, 925, 160, 70, 'Ingest Lambda', ['Idempotent upsert;', 'data version + 1'], 'compute', 'aws')
p.box('idq', 1050, 940, 140, 40, 'DLQ: ingest', [], 'integ', 'aws')

p.box('dp', 55, 750, 170, 60, 'CRO Data Product', ['Flag = Y claims only;', 'summary inputs only'], 'snow', 'snow')
p.box('st', 55, 840, 170, 60, 'Stream', ['Change capture on the', 'data product'], 'snow', 'snow')
p.box('sm', 255, 840, 170, 60, 'Summary table', ['Writeback for reporting', 'and audit queries'], 'snow', 'snow')
p.box('tk', 55, 925, 170, 70, 'Task', ['Runs only when stream', 'has data; no business rules'], 'snow', 'snow')
p.box('ob', 255, 925, 170, 70, 'Outbox table', ['Consumes stream;', 'COPY INTO S3 stage'], 'snow', 'snow')

p.box('wf', 1340, 160, 300, 50, 'Workload Identity Federation', ['Keyless: AWS IAM role to GCP service account'], 'gcp', 'gcp')
p.box('cr', 1340, 240, 140, 70, 'B: Cloud Run front', ['Verifies caller, policy,', 'logging; invokes agent'], 'gcp', 'gcp')
p.box('ae', 1500, 240, 140, 70, 'Agent Engine', ['Vertex AI; ADK summary', 'agent; data passed in'], 'gcp', 'gcp')
p.box('gm', 1500, 350, 140, 50, 'Gemini model', ['Summary generation'], 'gcp', 'gcp')
p.box('tr', 1340, 350, 140, 50, 'Trace + Logging', ['Audit trail'], 'gcp', 'gcp')
p.box('opt', 1340, 430, 300, 140, 'Open decision (DAIO to confirm)', ['A: worker invokes Agent Engine directly', 'with the WIF token; fewest parts.', 'B: worker invokes a Cloud Run service that', 'verifies the token, applies GCP-side policy', '(caller allow-list, size caps, screening)', 'and routes to Agent Engine. One GCP-owned', 'chokepoint for all AI calls.'], 'mgmt', 'gcp')

p.edge('hd', 'sso', [(60, 240), (45, 240), (45, 455), (60, 455)], dashed=True)
p.edge('cih', 'med', [(225, 312), (235, 312)])
p.edge('med', 'apic', [(400, 330), (440, 330), (440, 400), (485, 400)])
p.edge('apic', 'gw', [(555, 370), (555, 350)])
p.edge('dx', 'gw', [(400, 182), (445, 182), (445, 300), (485, 300)])
p.edge('gw', 's3ui', [(555, 270), (555, 220)])
p.edge('gw', 'authz', [(625, 310), (645, 310)])
p.edge('authz', 'al', [(785, 310), (805, 310)])
p.edge('al', 'ps', [(875, 270), (875, 220)], dashed=True)
p.edge('authz', 'db', [(715, 350), (715, 440)], dashed=True)
p.edge('al', 'db', [(875, 350), (875, 440)], both=True)
p.edge('al', 'gq', [(945, 310), (965, 310)])
p.edge('gq', 'gd', [(1050, 350), (1050, 400)], dashed=True)
p.edge('gq', 'wk', [(1105, 310), (1125, 310)])
p.edge('wk', 's3', [(1210, 350), (1210, 560)])
p.edge('wk', 'db', [(1140, 350), (1140, 520), (945, 520)])
p.edge('wk', 'wf', [(1265, 278), (1282, 278), (1282, 185), (1340, 185)], dashed=True)
p.edge('wk', 'cr', [(1265, 305), (1340, 305)])
p.edge('wk', 'ae', [(1265, 292), (1305, 292), (1305, 228), (1570, 228), (1570, 240)])
p.edge('cr', 'ae', [(1480, 275), (1500, 275)])
p.edge('ae', 'gm', [(1570, 310), (1570, 350)])
p.edge('ae', 'tr', [(1500, 300), (1490, 300), (1490, 375), (1480, 375)], dashed=True)
p.edge('dp', 'st', [(140, 810), (140, 840)])
p.edge('st', 'tk', [(140, 900), (140, 925)])
p.edge('tk', 'ob', [(225, 960), (255, 960)])
p.edge('ob', 'sl', [(425, 960), (485, 960)])
p.edge('sl', 'iq', [(625, 960), (660, 960)])
p.edge('iq', 'il', [(810, 960), (850, 960)])
p.edge('il', 'idq', [(1010, 960), (1050, 960)], dashed=True)
p.edge('il', 'db', [(930, 925), (930, 760), (795, 760), (795, 640)])
p.edge('s3', 'sm', [(1180, 630), (1180, 720), (450, 720), (450, 870), (425, 870)], dashed=True)

for t, x, y in [('1', 445, 240), ('2', 580, 245), ('3', 45, 375), ('F', 440, 365), ('4', 635, 258), ('5', 795, 258), ('6', 955, 258),
                ('7', 1115, 258), ('8', 1305, 258), ('A', 1440, 228), ('B', 1302, 305), ('9', 1570, 330), ('10', 1040, 520)]:
    p.badge(t, x, y)
for t, x, y in [('A', 162, 825), ('B', 455, 960), ('C', 830, 945), ('D', 930, 860), ('E', 600, 720)]:
    p.badge(t, x, y, TEAL)
p.notes(1310, 600, 360, 490, NOTES + ['F   CIH -> mediation -> Apigee -> same gateway and API'])
p.legend(30, 530, 400, 140, [('flow', 'Call / data flow'), ('dashed', 'Identity, config, error or optional'),
                             ('badge', '1', NAVY, 'Request path step'), ('badge', 'A', TEAL, 'Ingest path step'), ('col',),
                             ('swatch', '#ED7100', 'Compute'), ('swatch', '#3F8624', 'Storage'), ('swatch', '#3B48CC', 'Database'),
                             ('swatch', '#E7157B', 'Messaging / API'), ('swatch', '#DD344C', 'Security / identity')])

# =====================================================================
# Page 2: deployment
# =====================================================================
q = d.page('2 - Deployment', 'CRO: On-Demand Claim Summary - Deployment Architecture', 1700, 1150, 'deployment')
q.group('idp', 30, 100, 300, 170, 'Microsoft Entra ID', 'custom', color='#0078D4', corner='custom:entra')
q.group('prem', 30, 310, 300, 190, 'HIG network (on premises)', 'on_prem')
q.group('cio', 30, 540, 300, 150, 'CIO services (AWS)', 'custom', color='#5F6B7A', corner='custom:app')
q.group('sf', 30, 730, 300, 370, 'Snowflake', 'custom', color='#29B5E8', corner='custom:snowflake')
q.group('aws', 380, 100, 900, 1010, 'AWS Cloud (LOB CloudOps account)', 'aws_cloud')
q.group('reg', 410, 140, 840, 960, 'Region us-east-1', 'region', parent='aws')
q.group('vpc', 440, 180, 790, 330, 'VPC: private subnets, 2 AZs', 'vpc', parent='reg')
q.group('gcp', 1310, 100, 360, 490, 'Google Cloud: options A / B', 'custom', color='#4285F4', corner='custom:gcp')
q.group('ddb', 640, 560, 340, 180, 'Amazon DynamoDB: CRO state', 'custom', parent='reg', color='#C925D1', corner='aws:dynamodb')

q.icon('sso', 100, 190, 'custom:entra', 'Azure AD', 'SSO, PKCE, PRT', 'idp')
q.icon('adg', 230, 190, 'custom:adgroup', 'AD group', 'CRO-Handlers', 'idp')
q.icon('hd', 250, 400, 'custom:person', 'Claim handler', 'HIG-joined device', 'prem')
q.icon('dx', 100, 400, 'aws:direct_connect', 'Direct Connect', 'Private link', 'prem')
q.icon('cih', 100, 620, 'custom:app', 'Claims Insights Hub', 'future host', 'cio')
q.icon('med', 250, 620, 'custom:app', 'Mediation layer', 'Apigee consumer', 'cio')
q.icon('apic', 500, 400, 'custom:apigee', 'Apigee', 'API key + mTLS', 'vpc')

q.icon('ep', 500, 250, 'aws:vpc_privatelink', 'VPC endpoint', 'execute-api', 'vpc')
q.icon('gw', 630, 250, 'aws:api_gateway', 'Private API Gateway', 'Custom domain', 'vpc')
q.icon('authz', 760, 250, 'aws:lambda', 'Lambda Authorizer', 'JWT + AD group', 'vpc')
q.icon('al', 890, 250, 'aws:lambda', 'AWS Lambda', 'API handler', 'vpc')
q.icon('gq', 1020, 250, 'aws:sqs', 'Amazon SQS', 'Generation queue', 'vpc')
q.icon('wk', 1150, 250, 'aws:lambda', 'AWS Lambda', 'Summary worker', 'vpc')
q.icon('s3ui', 630, 400, 'aws:s3', 'Amazon S3', 'UI bundle (static)', 'vpc')
q.icon('ps', 760, 400, 'aws:systems_manager', 'Parameter Store', 'Thresholds', 'vpc')
q.icon('gd', 1020, 400, 'aws:sqs', 'Amazon SQS', 'Generation DLQ', 'vpc')
q.icon('kms', 500, 640, 'aws:key_management_service', 'AWS KMS', 'CMKs', 'reg')
q.icon('i1', 700, 630, 'custom:ddb_item', 'Current claim', 'item', 'ddb')
q.icon('i2', 800, 630, 'custom:ddb_item', 'Summary items', '(versioned)', 'ddb')
q.icon('i4', 900, 630, 'custom:ddb_item', 'In-flight', 'lock', 'ddb')
q.icon('s3', 1150, 800, 'aws:s3', 'Amazon S3', 'Snapshots + summaries', 'reg')
q.icon('sl', 474, 900, 'aws:s3', 'Amazon S3', 'Landing', 'reg')
q.icon('iq', 624, 900, 'aws:sqs', 'Amazon SQS', 'Ingest queue', 'reg')
q.icon('idq', 624, 1020, 'aws:sqs', 'Amazon SQS', 'Ingest DLQ', 'reg')
q.icon('il', 784, 900, 'aws:lambda', 'AWS Lambda', 'Ingest function', 'reg')
q.icon('r53', 860, 1020, 'aws:route_53', 'Route 53', 'Private hosted zone', 'reg')
q.icon('acm', 975, 1020, 'aws:certificate_manager_3', 'ACM', 'TLS certificates', 'reg')
q.icon('ct', 1090, 1020, 'aws:cloudtrail', 'CloudTrail', 'API audit', 'reg')
q.icon('cw', 1200, 1020, 'aws:cloudwatch_2', 'CloudWatch', 'Logs to Splunk', 'reg')

q.icon('dp', 100, 800, 'custom:sf_table', 'CRO Data Product', 'Flag = Y claims', 'sf')
q.icon('st', 100, 910, 'custom:sf_stream', 'Stream', 'Change capture', 'sf')
q.icon('tk', 100, 1030, 'custom:sf_task', 'Task', 'Unload to S3 stage', 'sf')
q.icon('sm', 250, 960, 'custom:sf_table', 'Summary table', 'Reporting writeback', 'sf')

q.icon('wf', 1370, 200, 'gcp:Cloud IAM', 'Workload Identity', 'Federation (keyless)', 'gcp')
q.icon('cr', 1370, 340, 'gcp:Cloud Run', 'B: Cloud Run front', 'verify, policy, route', 'gcp')
q.icon('ae', 1510, 340, 'gcp:Vertex AI', 'Agent Engine', 'ADK summary agent', 'gcp')
q.icon('gm', 1630, 340, 'custom:gemini', 'Gemini', 'Model', 'gcp')
q.icon('tr', 1510, 480, 'gcp:Trace', 'Cloud Trace + Logging', 'Audit trail', 'gcp')

q.edge('adg', 'sso', [(206, 190), (124, 190)], dashed=True)
q.edge('hd', 'sso', [(250, 376), (250, 290), (100, 290), (100, 254)], dashed=True)
q.edge('hd', 'dx', [(226, 400), (124, 400)])
q.edge('dx', 'ep', [(100, 464), (100, 475), (425, 475), (425, 250), (476, 250)])
q.edge('ep', 'gw', [(524, 250), (606, 250)])
q.edge('gw', 's3ui', [(630, 314), (630, 376)])
q.edge('gw', 'authz', [(654, 250), (736, 250)])
q.edge('authz', 'sso', [(760, 226), (760, 132), (100, 132), (100, 166)], dashed=True)
q.edge('authz', 'al', [(784, 250), (866, 250)])
q.edge('authz', 'ddb', [(748, 314), (748, 350), (700, 350), (700, 560)], dashed=True)
q.edge('al', 'ps', [(890, 314), (890, 350), (772, 350), (772, 376)], dashed=True)
q.edge('al', 'ddb', [(902, 314), (902, 560)], both=True)
q.edge('al', 'gq', [(914, 250), (996, 250)])
q.edge('gq', 'gd', [(1020, 314), (1020, 376)], dashed=True)
q.edge('gq', 'wk', [(1044, 250), (1126, 250)])
q.edge('wk', 's3', [(1150, 314), (1150, 776)])
q.edge('wk', 'ddb', [(1138, 314), (1138, 620), (980, 620)])
q.edge('wk', 'wf', [(1174, 250), (1260, 250), (1260, 200), (1346, 200)], dashed=True)
q.edge('wk', 'cr', [(1162, 314), (1162, 340), (1346, 340)])
q.edge('wk', 'ae', [(1174, 262), (1300, 262), (1300, 300), (1510, 300), (1510, 316)])
q.edge('cr', 'ae', [(1394, 340), (1486, 340)])
q.edge('ae', 'gm', [(1534, 340), (1606, 340)])
q.edge('ae', 'tr', [(1510, 404), (1510, 456)], dashed=True)
q.edge('dp', 'st', [(100, 864), (100, 886)])
q.edge('st', 'tk', [(100, 974), (100, 1006)])
q.edge('tk', 'sl', [(124, 1030), (420, 1030), (420, 900), (450, 900)])
q.edge('sl', 'iq', [(498, 900), (600, 900)])
q.edge('iq', 'il', [(648, 900), (760, 900)])
q.edge('iq', 'idq', [(624, 964), (624, 996)], dashed=True)
q.edge('il', 'ddb', [(784, 876), (784, 740)])
q.edge('cih', 'med', [(124, 620), (226, 620)])
q.edge('med', 'apic', [(250, 596), (250, 570), (350, 570), (350, 520), (500, 520), (500, 464)])
q.edge('apic', 'gw', [(524, 388), (560, 388), (560, 262), (606, 262)])
q.edge('s3', 'sm', [(1126, 800), (380, 800), (380, 960), (274, 960)], dashed=True)

for t, x, y in [('1', 380, 475), ('2', 630, 345), ('3', 175, 290), ('4', 565, 250), ('5', 695, 250), ('6', 825, 250),
                ('7', 955, 250), ('8', 1230, 262), ('A', 1420, 300), ('B', 1250, 340), ('9', 1570, 340), ('10', 1060, 620),
                ('A', 100, 875), ('B', 420, 965), ('F', 300, 570), ('C', 549, 900), ('D', 784, 808), ('E', 600, 800)]:
    q.badge(t, x, y)
q.notes(1310, 620, 360, 510, NOTES + ['F   CIH -> mediation -> Apigee -> same gateway and API', 'Dashed line: identity, config, error or optional'])

# =====================================================================
# Page 3: access control model (AD group only)
# =====================================================================
r = d.page('3 - Access control', 'CRO: Access Control Model', 1700, 760, 'conceptual')
r.panel('idp', 30, 120, 400, 220, 'Microsoft Entra ID (owned by IAM)', 'azure')
r.panel('aws', 470, 120, 810, 400, 'AWS (owned by EDS Claims)', 'aws')
r.panel('cio', 30, 380, 400, 140, 'External consumers (owned by CIO)', 'neutral')

r.box('sso', 55, 170, 170, 70, 'Azure AD SSO', ['Who you are: PKCE,', 'device PRT, MFA, CA'], 'security', 'idp')
r.box('adg', 245, 170, 160, 70, 'AD group CRO-Handlers', ['May use CRO; membership', 'managed by IAM / access', 'request process'], 'security', 'idp')
r.box('token', 55, 260, 350, 50, 'Access token (JWT)', ['sub, upn, aud = CRO API, exp, groups'], 'security', 'idp')
r.box('cih', 55, 430, 170, 70, 'Claims Insights Hub', ['Owns its screen and', 'any claim-level rules'], 'ext', 'cio')
r.box('med', 245, 430, 160, 70, 'Mediation layer', ['Service identity via', 'Apigee key + mTLS'], 'ext', 'cio')

r.box('ui', 500, 170, 150, 70, 'CRO SPA (MSAL.js)', ['Holds the token; shows', 'or hides UI only'], 'ext', 'aws')
r.box('gw', 680, 170, 160, 70, 'Private API Gateway', ['Invokes authorizer', 'on every request'], 'integ', 'aws')
r.box('authz', 870, 170, 190, 70, 'Lambda Authorizer', ['L2: signature, iss, aud, exp', '+ groups has CRO-Handlers'], 'security', 'aws')
r.box('al', 1090, 170, 160, 70, 'API Lambda', ['Runs only on Allow;', 'no identity checks inside'], 'compute', 'aws')
r.box('apg', 680, 300, 160, 70, 'Apigee product', ['Service callers: key +', 'client cert; read-only'], 'integ', 'aws')
r.box('audit', 870, 300, 380, 90, 'L3: audit log', ['Every call: user or service, claim, summary version,', 'allow / deny, time. CloudWatch to Splunk; CloudTrail', 'for control-plane activity. Retained per HIG standard.'], 'mgmt', 'aws')
r.box('scope', 500, 410, 750, 90, 'Scope decision (business-approved)', ['Any member of CRO-Handlers may request and view a summary for any flagged claim.', 'No claim-level restriction in CRO. If ClaimCenter secured-claim rules must apply, the consumer', 'that owns the handler screen (CIH) enforces them; CRO exposes the data needed to do so.'], 'ext', 'aws')

r.edge('sso', 'token', [(140, 240), (140, 260)])
r.edge('adg', 'token', [(325, 240), (325, 260)])
r.edge('token', 'ui', [(405, 285), (575, 285), (575, 240)], dashed=True)
r.edge('ui', 'sso', [(500, 190), (450, 190), (450, 150), (140, 150), (140, 170)], dashed=True)
r.edge('ui', 'gw', [(650, 205), (680, 205)])
r.edge('gw', 'authz', [(840, 205), (870, 205)])
r.edge('authz', 'al', [(1060, 205), (1090, 205)])
r.edge('authz', 'audit', [(965, 240), (965, 300)], dashed=True)
r.edge('al', 'audit', [(1170, 240), (1170, 300)])
r.edge('med', 'apg', [(405, 465), (460, 465), (460, 335), (680, 335)])
r.edge('apg', 'gw', [(760, 300), (760, 240)])

for t, x, y in [('1', 300, 150), ('2', 490, 285), ('3', 665, 190), ('4', 855, 190), ('5', 1075, 190), ('6', 1170, 270)]:
    r.badge(t, x, y)
for t, x, y in [('F', 460, 400)]:
    r.badge(t, x, y, TEAL)
r.notes(1310, 120, 360, 480, [
    ('h', 'THREE LAYERS'),
    'L1  Authentication: Azure AD SSO. No local',
    '     accounts, no passwords in CRO.',
    'L2  Authorization: membership of AD group',
    '     CRO-Handlers, read from the token and',
    '     enforced in the Lambda Authorizer before',
    '     any business code runs.',
    'L3  Audit: every allow / deny logged.',
    ('h', 'FLOW'),
    '1   SPA starts PKCE login; device SSO',
    '2   Token returned (groups claim included)',
    '3   Every API call carries the bearer token',
    '4   Gateway invokes the authorizer',
    '5   Allow: IAM policy admits the call',
    '6   Decision logged',
    'F   Service callers authenticate via Apigee;',
    '     same gateway, read-only policy',
    ('h', 'WHAT IS NOT HERE, AND WHY'),
    'No claim-level entitlement check. Business',
    'scope is "all CRO-Handlers, all flagged',
    'claims". Adding it later is an authorizer',
    'change plus a data feed, not a redesign.',
    ('h', 'REVOCATION'),
    'Remove the user from the AD group: access',
    'ends at next token refresh (<= 1 hour).',
])
r.legend(470, 560, 810, 90, [('flow', 'Call / data flow'), ('dashed', 'Identity / token exchange'), ('col',),
                              ('badge', '1', NAVY, 'Request path step'), ('badge', 'F', TEAL, 'External consumer path')])

# =====================================================================
# Page 4: authentication and authorization sequence
# =====================================================================
s = d.page('4 - Auth sequence', 'CRO: Authentication and API Authorization Sequence (pattern section 4)', 1700, 880, 'conceptual')
PART = [('hd', 100, 'Claim handler', 'HIG-joined device', 'ext'), ('spa', 270, 'SPA (browser)', 'MSAL.js', 'ext'),
        ('gw', 440, 'Private API Gateway', 'VPC endpoint', 'integ'), ('s3', 610, 'S3: UI bundle', 'static', 'storage'),
        ('aad', 780, 'Azure AD', 'Entra ID', 'security'), ('az', 950, 'Lambda Authorizer', 'L2 + L3', 'security'),
        ('db', 1120, 'DynamoDB', 'CRO state', 'db'), ('al', 1290, 'API Lambda', 'summary API', 'compute')]
X = {}
for i, x, t, sub, k in PART:
    X[i] = x
    s.box(i, x - 70, 130, 140, 50, t, [sub], k)
    s.box(i + '_l', x - 1, 180, 2, 640, '', [], 'mgmt')
MSG = [(210, 'hd', 'spa', 0, '1'), (240, 'spa', 'gw', 0, '2'), (270, 'gw', 's3', 0, '3'), (300, 's3', 'spa', 1, ''),
       (340, 'spa', 'aad', 0, '4'), (370, 'aad', 'spa', 1, '5'),
       (410, 'spa', 'gw', 0, '6'), (440, 'gw', 'az', 0, '7'), (470, 'az', 'aad', 1, '7a'), (510, 'az', 'gw', 1, '7c'), (550, 'gw', 'spa', 1, '8'),
       (630, 'gw', 'al', 0, '9'), (660, 'al', 'db', 0, '10'), (690, 'db', 'al', 1, ''), (720, 'al', 'gw', 1, ''),
       (750, 'gw', 'spa', 1, '11'), (780, 'spa', 'hd', 1, '12')]
for y, a, b, dsh, t in MSG:
    s.edge(a + '_l', b + '_l', [(X[a], y), (X[b], y)], dashed=bool(dsh))
    if t:
        s.badge(t, (X[a] + X[b]) / 2, y - 14)
s.notes(1400, 130, 270, 690, [
    ('h', 'STATIC PATH'),
    '1   Handler opens app.<domain>',
    '2   Over Direct Connect to the private',
    '     API Gateway (VPC endpoint)',
    '3   Gateway proxies /app to S3',
    '     (deviation: no Fargate web tier)',
    '     Bundle returned; SPA starts',
    ('h', 'AUTHENTICATION'),
    '4   MSAL.js: authorization code + PKCE',
    '     Azure AD uses the device PRT; no',
    '     prompt on a HIG-joined device',
    '5   JWT access token with claims',
    ('h', 'API AUTHORIZATION'),
    '6   GET /summary/{claim}, bearer token',
    '7   Gateway invokes Lambda Authorizer',
    '7a  JWKS from Azure AD (cached); checks',
    '     signature, iss, aud, exp, group',
    '7b  groups claim contains CRO-Handlers',
    '7c  IAM policy Allow / Deny returned',
    '8   Deny: 401/403 to the SPA',
    ('h', 'BUSINESS CALL'),
    '9   Allow: API Lambda invoked directly',
    '     (no VPC Link; Lambda backend)',
    '10  Eligibility, version compare, lock,',
    '     stored summary or enqueue',
    '11  200 summary or 202 queued',
    '12  SPA renders; polls if queued',
    ('h', 'NOTES'),
    'Dashed arrows are responses.',
    'Token validation is stateless; only',
    'the JWKS document is cached.',
    'The PRT is never seen by the SPA.',
])

# =====================================================================
# Page 5: security detail (pattern SPA_Internal_04 conventions)
# =====================================================================
v = d.page('5 - Security detail', 'CRO: Security Flow Detail (HIG pattern SPA_Internal_04 conventions)', 1700, 1000, 'deployment')
v.group('dc', 30, 110, 330, 360, 'HIG corporate network', 'custom', color='#5F6B7A', corner='custom:person')
v.group('idp', 30, 510, 330, 165, 'Microsoft Entra ID (Azure AD)', 'custom', color='#0078D4', corner='custom:entra')
v.group('cio', 30, 710, 330, 125, 'CIO services (AWS)', 'custom', color='#5F6B7A', corner='custom:app')
v.group('aws', 400, 110, 940, 760, 'AWS Cloud: LOB CloudOps account', 'aws_cloud')
v.group('reg', 430, 150, 880, 690, 'Region us-east-1', 'region', parent='aws')
v.group('vpc', 460, 270, 820, 540, 'VPC: Private API Gateway front door', 'vpc', parent='reg')
v.group('az', 720, 320, 530, 460, 'Availability Zone (x2)', 'custom', parent='vpc', color='#147EBA')
v.group('sub', 750, 370, 470, 380, 'Application subnet (private)', 'custom', parent='az', color='#ED7100')

v.icon('u1', 80, 220, 'custom:person', 'Handler', 'PRT 1', 'dc')
v.icon('u2', 160, 220, 'custom:person', 'Handler', 'PRT 2', 'dc')
v.icon('u3', 240, 220, 'custom:person', 'Handler', 'PRT 3', 'dc')
v.icon('dx', 240, 390, 'aws:direct_connect', 'AWS Direct Connect', 'HIG to AWS backbone', 'dc')
v.icon('aad', 110, 590, 'custom:entra', 'Azure AD', 'OAuth 2.0 + PKCE', 'idp')
v.icon('adg', 270, 590, 'custom:adgroup', 'AD group', 'CRO-Handlers', 'idp')
v.icon('cih', 100, 790, 'custom:app', 'Claims Insights Hub', 'consumer', 'cio')
v.icon('med', 260, 790, 'custom:app', 'Mediation layer', 'Apigee consumer', 'cio')

v.icon('ep', 560, 390, 'aws:vpc_privatelink', 'VPC endpoint', 'execute-api (PrivateLink)', 'vpc')
v.icon('gw', 560, 560, 'aws:api_gateway', 'Private API Gateway', 'api./app.cro.<domain>', 'vpc')
v.icon('apic', 490, 730, 'custom:apigee', 'Apigee', 'API key + mTLS', 'vpc')
v.icon('s3ui', 830, 440, 'aws:s3', 'S3: SPA bundle', 'static (D1)', 'sub')
v.icon('al', 1130, 440, 'aws:lambda', 'Application API', 'on Lambda', 'sub')
v.icon('authz', 830, 660, 'aws:lambda', 'Lambda Authorizer', 'VPC-enabled, stateless', 'sub')
v.icon('ddb', 1130, 660, 'aws:dynamodb', 'DynamoDB', 'CRO state (API only)', 'sub')
v.icon('r53', 1030, 210, 'aws:route_53', 'Route 53', 'private zone', 'reg')
v.icon('acm', 1130, 210, 'aws:certificate_manager_3', 'ACM', 'TLS 1.2+', 'reg')
v.icon('cw', 1230, 210, 'aws:cloudwatch_2', 'CloudWatch', 'to Splunk', 'reg')
v.icon('ct', 520, 210, 'aws:cloudtrail', 'CloudTrail', 'API audit', 'reg')
v.icon('iam', 620, 210, 'aws:identity_and_access_management', 'IAM', 'policies', 'reg')
v.icon('kms', 720, 210, 'aws:key_management_service', 'KMS', 'CMKs', 'reg')

# browser -> Direct Connect -> VPC endpoint: static (1) and dynamic (6) drawn as two parallel lines
v.edge('u3', 'dx', [(240, 284), (240, 366)])
v.edge('dx', 'ep', [(264, 378), (420, 378), (420, 378), (536, 378)])                        # 1 static
v.edge('dx', 'ep', [(264, 402), (536, 402)])                                                # 6 dynamic
v.edge('ep', 'gw', [(560, 454), (560, 536)])
v.edge('gw', 's3ui', [(584, 548), (680, 548), (680, 440), (806, 440)])                      # 2 static
v.edge('gw', 'al', [(584, 572), (1000, 572), (1000, 440), (1106, 440)])          # 9 / 10
v.edge('gw', 'authz', [(548, 624), (548, 660), (806, 660)])                                 # 7
v.edge('authz', 'gw', [(830, 636), (830, 630), (575, 630), (575, 624)], dashed=True)        # 7c policy back
v.edge('authz', 'aad', [(818, 724), (818, 848), (15, 848), (15, 580), (86, 580)], dashed=True)  # 7a JWKS
v.edge('u1', 'aad', [(80, 284), (80, 500), (98, 500), (98, 566)], dashed=True)              # 3 PKCE
v.edge('aad', 'u2', [(122, 566), (122, 520), (160, 520), (160, 284)], dashed=True)          # 5 JWT back
v.edge('adg', 'aad', [(246, 600), (134, 600)], dashed=True)
v.edge('cih', 'med', [(124, 790), (236, 790)])
v.edge('med', 'apic', [(284, 790), (440, 790), (440, 730), (466, 730)])                     # F
v.edge('apic', 'gw', [(490, 706), (490, 560), (536, 560)])

for t, x, y in [('1', 340, 378), ('6', 420, 402), ('2', 680, 500), ('3', 80, 380), ('5', 160, 380), ('4', 60, 540),
                ('7', 680, 660), ('7a', 420, 848), ('7b', 690, 690), ('7c', 700, 630), ('8', 560, 500),
                ('9', 800, 572), ('10', 1000, 500), ('F', 350, 790)]:
    v.badge(t, x, y)
v.notes(1370, 110, 300, 760, [
    ('h', 'NUMBERING = PATTERN SECTION 4'),
    '1   User opens https://app.cro.<domain>',
    '     TLS 1.2 : 443 over Direct Connect',
    '2   Gateway serves SPA bundle from S3',
    '     (D1: no Fargate web tier / ALB)',
    '3   SPA starts OAuth 2.0 auth code +',
    '     PKCE with Azure AD (MSAL.js);',
    '     browser SSO context from device PRT',
    '4   Azure AD validates user + device,',
    '     MFA / Conditional Access',
    '5   Azure AD returns JWT access token',
    '6   SPA calls https://api.cro.<domain>',
    '     Authorization: Bearer <JWT>',
    '     TLS 1.2 : 443 via VPC endpoint',
    '7   Gateway invokes Lambda Authorizer',
    '7a  Validate JWT: JWKS signature, iss,',
    '     aud, exp, groups (CRO-Handlers)',
    '7b  Authorization: groups claim must',
    '     (D2: inside authorizer, not a',
    '     separate Authorize API)',
    '7c  Return IAM policy Allow / Deny',
    '8   Gateway evaluates policy; 401/403',
    '     on Deny; policy cached per token',
    '9   Allowed request to Lambda API',
    '     directly (no VPC Link / ALB)',
    '10  Response through the gateway',
    ('h', 'EXTERNAL CONSUMER PATH'),
    'F   CIH -> mediation -> Apigee (API key',
    '     + mTLS) -> same gateway and API.',
    '     Service identity; read-only policy.',
    '     Claim-level rules, if any, live in CIH.',
    ('h', 'CONTROLS'),
    'No internet route; private DNS only',
    'Gateway resource policy: VPC endpoint',
    '  and Apigee source only',
    'Security groups: inbound only from',
    '  the gateway path',
    'PRT never read, stored or forwarded',
    'Stateless token validation; JWKS cached',
    'Decisions logged: CloudWatch -> Splunk;',
    '  CloudTrail for API activity',
    'Azure AD only; no ADFS (open item 2)',
])
v.legend(400, 890, 940, 90, [('flow', 'Request / data flow'), ('dashed', 'Identity, token or policy exchange'), ('col',),
                              ('badge', '7a', '#000000', 'Step per pattern section 4'), ('badge', 'F', '#000000', 'External consumer path')])

# =====================================================================
# Page 6: disaster recovery (mandatory page)
# =====================================================================
w = d.page('6 - Disaster recovery', 'CRO: Disaster Recovery - Pilot Light (Cold Standby)', 1700, 880, 'deployment')
w.group('prem', 30, 110, 300, 200, 'HIG network', 'on_prem')
w.group('aws', 370, 110, 970, 680, 'AWS Cloud (LOB CloudOps account)', 'aws_cloud')
w.group('p', 400, 200, 440, 560, 'Primary: us-east-1 (active)', 'region', parent='aws')
w.group('s', 880, 200, 440, 560, 'Secondary: us-east-2 (pilot light)', 'region', parent='aws')
w.group('gcp', 30, 360, 300, 200, 'Google Cloud (multi-region)', 'custom', color='#4285F4', corner='custom:gcp')

w.icon('hd', 100, 220, 'custom:person', 'Claim handler', 'app./api.cro.<domain>', 'prem')
w.icon('r53', 230, 220, 'aws:route_53', 'Route 53', 'failover records', 'prem')
w.icon('ae', 180, 470, 'gcp:Vertex AI', 'Agent Engine', 'regional; GCP DR separate', 'gcp')

w.icon('pgw', 480, 300, 'aws:api_gateway', 'Private API GW', 'deployed', 'p')
w.icon('pau', 620, 300, 'aws:lambda', 'Authorizer + API', 'deployed', 'p')
w.icon('pq', 760, 300, 'aws:sqs', 'SQS', 'deployed', 'p')
w.icon('pin', 480, 470, 'aws:s3', 'S3 landing', 'Snowflake unload', 'p')
w.icon('ps3', 620, 470, 'aws:s3', 'S3 snapshots + UI', 'CRR source', 'p')
w.icon('pdb', 760, 470, 'aws:dynamodb', 'DynamoDB', 'global table (active)', 'p')
w.icon('pep', 480, 640, 'aws:vpc_privatelink', 'VPC endpoint', 'deployed', 'p')
w.icon('ptf', 620, 640, 'aws:cloudformation', 'Terraform state', 'pipeline', 'p')
w.icon('pkms', 760, 640, 'aws:key_management_service', 'KMS', 'multi-region key', 'p')

w.icon('sdb', 960, 470, 'aws:dynamodb', 'DynamoDB', 'global table replica', 's')
w.icon('ss3', 1100, 470, 'aws:s3', 'S3 snapshots + UI', 'CRR destination', 's')
w.icon('sin', 1240, 470, 'aws:s3', 'S3 landing', 'failover unload target', 's')
w.icon('sgw', 960, 300, 'aws:api_gateway', 'Private API GW', 'pre-provisioned, idle', 's')
w.icon('sau', 1100, 300, 'aws:lambda', 'Authorizer + API', 'pre-provisioned, idle', 's')
w.icon('sq', 1240, 300, 'aws:sqs', 'SQS', 'pre-provisioned', 's')
w.icon('skms', 960, 640, 'aws:key_management_service', 'KMS', 'replica key', 's')
w.icon('stf', 1100, 640, 'aws:cloudformation', 'Terraform apply', 'scale-up on failover', 's')
w.icon('sep', 1240, 640, 'aws:vpc_privatelink', 'VPC endpoint', 'pre-provisioned', 's')

w.edge('hd', 'r53', [(124, 220), (206, 220)])
w.edge('r53', 'pgw', [(254, 212), (340, 212), (340, 290), (456, 290)])
w.edge('r53', 'sgw', [(230, 196), (230, 180), (900, 180), (900, 290), (936, 290)], dashed=True)
w.edge('pdb', 'sdb', [(784, 470), (936, 470)], both=True)
w.edge('ps3', 'ss3', [(620, 534), (620, 545), (1100, 545), (1100, 534)])
w.edge('pkms', 'skms', [(784, 640), (936, 640)], dashed=True)
w.edge('ptf', 'stf', [(620, 704), (620, 740), (1100, 740), (1100, 704)], dashed=True)
w.edge('pau', 'ae', [(608, 364), (608, 400), (360, 400), (360, 460), (204, 460)])
w.edge('sau', 'ae', [(1112, 364), (1112, 420), (380, 420), (380, 484), (204, 484)], dashed=True)
for t, x, y in [('1', 300, 212), ('2', 860, 470), ('3', 860, 545), ('4', 860, 640), ('5', 860, 740), ('6', 600, 180)]:
    w.badge(t, x, y)
w.notes(1370, 110, 300, 680, [
    ('h', 'STRATEGY'),
    'Pilot Light (Cold Standby) per the',
    'application metal tier (to confirm).',
    'RTO / RPO: from the tier (open item 1).',
    ('h', 'REPLICATED CONTINUOUSLY'),
    '2  DynamoDB global table: claim items,',
    '    summaries, locks',
    '3  S3 cross-region replication: model',
    '    input snapshots, summaries, UI bundle',
    '4  KMS multi-region key; replica in',
    '    secondary so replicated data decrypts',
    ('h', 'PRE-PROVISIONED, IDLE'),
    'Private API Gateway, VPC endpoint,',
    'Lambda Authorizer, API Lambda, SQS,',
    'Route 53 secondary records, Apigee route',
    ('h', 'FAILOVER'),
    '5  Terraform pipeline scales secondary',
    '    (reserved concurrency, alarms, Splunk)',
    '1  Route 53 repoints app. and api. CNAME',
    '    / alias to the secondary endpoints',
    '    Snowflake task unload retargeted to',
    '    the secondary landing bucket',
    '6  Secondary serves; health checks on',
    '    primary gate automatic failback',
    ('h', 'FAILBACK'),
    'Restore primary, let global table and',
    'CRR converge, repoint Route 53, scale',
    'secondary back down.',
    ('h', 'OUT OF SCOPE HERE'),
    'Apigee DR: platform team',
    'Snowflake DR: platform team (SnowGrid)',
    'GCP: Agent Engine is regional; multi-',
    'region endpoint choice tracked on the',
    'GCP side (same as SIU)',
    ('h', 'TEST'),
    'Annual failover exercise in non-prod;',
    'runbook kept with the Terraform repo.',
])

# =====================================================================
# Page 7: pattern conformance
# =====================================================================
c = d.page('7 - Pattern conformance', 'CRO vs HIG Pattern SPA_Internal_04 v1: Conformance and Declared Deviations', 1700, 860, 'conceptual')
c.notes(30, 120, 400, 710, [
    ('h', 'ADOPTED AS WRITTEN'),
    'External consumers via Apigee product (API key +',
    '  mTLS), the standard EDS front door (enterprise API gateway)',
    'Users: HIG employees on HIG-joined devices, on the',
    'corporate network only',
    'All traffic over Direct Connect; no internet path',
    'Hosting in the LOB CloudOps account, us-east-1',
    'VPC with private subnets across 2 AZs',
    'Route 53 private hosted zone: app. and api. names',
    'ACM certificates; TLS 1.2+ on 443 everywhere',
    'Private REST API Gateway + execute-api VPC endpoint',
    '  + custom domain + resource policy',
    'API Gateway provisioned with the internal module',
    '  terraform-aws-apigateway-v1; no community modules',
    'SPA authenticates with MSAL.js, OAuth 2.0 auth code',
    '  + PKCE; no implicit flow, no client secret',
    'Azure AD SSO backed by the device PRT; the SPA never',
    '  reads, stores or forwards the PRT',
    'Lambda Authorizer, VPC-enabled, validates every',
    '  request: JWKS signature, issuer, audience, expiry,',
    '  group / role claims; stateless',
    'Authorizer returns a scoped IAM policy (Allow / Deny)',
    'Lambda APIs invoked directly by API Gateway',
    'Security groups: authorizer and Lambdas accept only',
    '  the API Gateway path; no inbound from elsewhere',
    'Tag-based IAM for administration of compute',
    'CloudWatch logs and metrics, forwarded to Splunk per',
    '  the HIG CloudWatch-to-Splunk design',
    'CloudTrail enabled for API activity audit',
    'Retries with exponential backoff and jitter',
    'Request metadata stored for idempotency (DynamoDB',
    '  in-flight lock and summary versions)',
    'Consistent error codes to consumers (401/403/404/',
    '  409 in-progress / 202 queued)',
    'HIG naming convention and mandatory tags',
    'Route 53 failover for DR; repoint app CNAME',
])
c.notes(460, 120, 560, 710, [
    ('h', 'ADAPTED: DEVIATION DECLARED WITH JUSTIFICATION'),
    'D1  Static content served from S3 through the private API Gateway',
    '    (HTTP proxy integration) instead of ECS Fargate + nginx + static ALB.',
    '    Why: the pattern itself (section 12, item 1) allows static delivery via',
    '    API Gateway. The CRO bundle is a few MB of HTML/JS/CSS with no server',
    '    logic. A container cluster across AZs adds patching, scaling, images',
    '    and cost while adding no control: the network boundary (VPC endpoint,',
    '    private DNS, Direct Connect) is identical. Fewer components, smaller',
    '    attack surface. Reversible: the bundle can move to Fargate later',
    '    without changing the SPA or the API.',
    '',
    'D2  No separate Authorize API; authorization is the AD group claim,',
    '    checked inside the Lambda Authorizer.',
    '    Why: the pattern calls the Authorize API "when needed". CRO\'s business',
    '    scope is "every CRO-Handlers member may see every flagged claim", so',
    '    the only rule is group membership, already in the token. A second',
    '    service would add a hop and a deployment with nothing to decide. The',
    '    authorizer still returns the scoped IAM policy the pattern requires.',
    '    Reversible: an Authorize API can be added if claim-level rules arrive.',
    '',
    'D3  Static content unauthenticated at the edge.',
    '    Why: permitted by the pattern (section 5) when the bundle holds no HIG',
    '    confidential or proprietary content. The CRO bundle contains UI code',
    '    only; all claim data is fetched through the authorized API path.',
    '    If a reviewer disagrees, the same gateway route can require the',
    '    bearer token with no architecture change.',
    '',
    'D4  DR scoped to the metal tier: Pilot Light (cold standby).',
    '    Why: CRO is a handler convenience tool, not a claims-processing',
    '    dependency. Terraform redeploys the Lambdas, authorizer and gateway',
    '    to the secondary region; DynamoDB uses a global table; S3 snapshot',
    '    bucket uses cross-region replication; Route 53 failover repoints',
    '    app. and api. names. RTO/RPO to be confirmed against the tier.',
    '',
    ('h', 'WHY THIS IS THE STRONGER POSITION'),
    'Each adaptation removes components rather than adding them. The security',
    'controls the pattern exists to enforce (private network, enterprise SSO,',
    'per-request token validation, scoped authorization, audit) are all',
    'present. What is removed is infrastructure that serves heavyweight',
    'ECS applications and would be idle in CRO.',
])
c.notes(1050, 120, 310, 710, [
    ('h', 'NOT APPLICABLE'),
    'VPC Link + internal API ALB',
    '  Pattern: Lambda APIs are',
    '  invoked directly; CRO has',
    '  no ECS / EKS / EC2 backend',
    'API ALB security group rules',
    '  No API ALB exists',
    'ECS target-tracking scaling,',
    '  task sizing, load tests',
    '  Replaced by Lambda reserved',
    '  concurrency and SQS caps',
    'Static ALB',
    '  Removed with D1',
    'On-premises ADFS',
    '  Assumed Azure AD only',
    '  (open item 2)',
    ('h', 'OUTSIDE THE PATTERN'),
    'Everything behind the API:',
    '  SQS, worker Lambda, DynamoDB,',
    '  S3 snapshots, KMS CMKs',
    'Snowflake ingest and writeback',
    'GCP: Agent Engine, Gemini,',
    '  Cloud Trace, WIF; option B',
    '  adds a Cloud Run front',
    'These follow the EDS Claims',
    'GenAI NFR patterns (Hot Path)',
    'and the earlier SIU review.',
])
c.notes(1390, 120, 280, 710, [
    ('h', 'OPEN ITEMS'),
    '1  Metal tier for CRO, and',
    '   the numeric RTO / RPO',
    '   that follow from it',
    '2  Confirm Azure AD only',
    '   (no ADFS) as target',
    '3  Confirm internal module',
    '   supports private REST',
    '   API + S3 proxy route',
    '4  Splunk index / log',
    '   retention for audit',
    '5  Reviewer acceptance of',
    '   D1 and D3; fallback is',
    '   Fargate + static ALB',
    '6  Business sign-off on',
    '   "all CRO-Handlers see',
    '   all flagged claims"',
    '7  GCP invocation: option',
    '   A (direct) or B (Cloud',
    '   Run front); DAIO call',
    '8  Mediation layer: does it',
    '   carry handler identity',
    '   for audit? (optional)',
    ('h', 'ASSUMPTIONS'),
    'Pilot: one LOB or office',
    'Handlers already in Azure',
    '  AD; group created by IAM',
    'Direct Connect and VPC',
    '  endpoints exist in the',
    '  LOB account (landing zone)',
])

base = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/CRO_Architecture_v0.6'
d.save(base)
