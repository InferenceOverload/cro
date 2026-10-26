#!/usr/bin/env python3
"""CRO v0.4: aligned to HIG pattern SPA_Internal_04 with declared deviations. Five pages."""
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

SUB = 'The Hartford EDS Claims  |  Draft for architecture review  |  v0.4 (pattern SPA_Internal_04)  |  2026-10-26'
d = Diagram(subtitle=SUB)
TEAL = '#0B7A75'
NAVY = '#1F4E79'

NOTES = [('h', 'REQUEST PATH'),
         '1   Handler opens app.<domain> over Direct Connect',
         '2   Private API Gateway serves the SPA bundle from S3',
         '3   MSAL.js: OAuth 2.0 + PKCE; Azure AD SSO (device PRT)',
         '4   Every API call carries the Azure AD access token',
         '5   Lambda Authorizer: JWT (JWKS, iss, aud, exp, group)',
         '     + entitlement ENT# vs CLAIM#; returns IAM policy',
         '6   API Lambda: flag = Y, age >= 30 days, version, lock',
         '7   Unchanged: return stored summary. Changed: enqueue',
         '8   Worker: snapshot to S3, Agent Engine via WIF',
         '9   Agent calls Gemini; trace logged',
         '10  Summary vN stored (append-only); lock released',
         ('h', 'INGEST PATH'),
         'A   Streams capture changes to claim and role products',
         'B   Task runs only when stream has data; unloads to S3',
         'C   S3 event to SQS; Ingest Lambda processes the batch',
         'D   Upserts claim items and handler entitlement items',
         'E   Summaries to Snowflake through Snowpipe (reporting)',
         ('h', 'SECURITY BASELINE'),
         'HIG pattern SPA_Internal_04; conformance on page 5',
         'No internet path; private DNS; ACM TLS 1.2+; KMS CMKs',
         'CloudTrail on; CloudWatch logs forwarded to Splunk',
         'Service clients: same gateway, client-credential tokens']

# =====================================================================
# Page 1: conceptual
# =====================================================================
p = d.page('1 - Conceptual', 'CRO: On-Demand Claim Summary - Solution Architecture', 1700, 1100, 'conceptual')
p.panel('net', 30, 110, 400, 170, 'HIG network (on premises)', 'neutral')
p.panel('idp', 30, 370, 400, 130, 'Microsoft Entra ID (Azure AD)', 'azure')
p.panel('snow', 30, 700, 400, 370, 'Snowflake', 'snow')
p.panel('aws', 460, 110, 820, 960, 'AWS (LOB CloudOps account, us-east-1)', 'aws')
p.panel('gcp', 1310, 110, 360, 480, 'GCP (all AI workload)', 'gcp')

p.box('dx', 60, 160, 340, 45, 'AWS Direct Connect', ['Private path to AWS; no internet routing'], 'ext', 'net')
p.box('hd', 60, 215, 340, 50, 'Claim handler', ['HIG-joined device; MSAL.js runs in the browser'], 'ext', 'net')
p.box('sso', 60, 415, 340, 70, 'Azure AD SSO (OAuth 2.0 + PKCE)', ['Device PRT, MFA, Conditional Access;', 'token carries AD group CRO-Handlers'], 'security', 'idp')

p.box('s3ui', 485, 160, 140, 60, 'S3: UI bundle', ['Static SPA assets;', 'no proprietary content'], 'storage', 'aws')
p.box('r53', 645, 160, 140, 60, 'Route 53 (private)', ['app./api.<domain>', 'private hosted zone'], 'mgmt', 'aws')
p.box('ps', 805, 160, 140, 60, 'Parameter Store', ['Thresholds, e.g.', 'min claim age = 30'], 'mgmt', 'aws')
p.box('acm', 965, 160, 140, 60, 'ACM certificates', ['TLS 1.2+ on 443'], 'security', 'aws')
p.box('ct', 1125, 160, 140, 60, 'CloudTrail', ['API activity audit'], 'security', 'aws')

p.box('gw', 485, 270, 140, 80, 'Private API Gateway', ['VPC endpoint, custom', 'domain, resource policy;', '/app proxied to S3'], 'integ', 'aws')
p.box('authz', 645, 270, 140, 80, 'Lambda Authorizer', ['Stateless JWT check via', 'Azure AD JWKS + group;', 'ENT# vs CLAIM# (page 3)'], 'security', 'aws')
p.box('al', 805, 270, 140, 80, 'API Lambda', ['Runs only on Allow;', 'eligibility, 30-day', 'rule, version, lock'], 'compute', 'aws')
p.box('gq', 965, 270, 140, 80, 'SQS: generation', ['Buffers jobs; caps', 'concurrency and cost'], 'integ', 'aws')
p.box('wk', 1125, 270, 140, 80, 'Worker Lambda', ['Snapshot, invoke agent,', 'store summary'], 'compute', 'aws')
p.box('gd', 980, 400, 140, 44, 'DLQ: generation', [], 'integ', 'aws')
p.box('cw', 485, 440, 140, 70, 'CloudWatch', ['Logs, metrics, alarms;', 'forwarded to Splunk'], 'mgmt', 'aws')
p.box('kms', 485, 540, 140, 60, 'KMS', ['Customer-managed keys', 'for S3 and DynamoDB'], 'security', 'aws')
p.box('db', 645, 440, 300, 200, 'DynamoDB: CRO state',
      ['Current claim item (1 per claim): payload or S3', 'pointer, eligibility, open date, data version', '',
       'Summary items (append-only): text, source version,', 'prompt + model version, trace ID, snapshot ref', '',
       'Handler entitlement item ENT#<user> (page 3)', 'In-flight lock (conditional write)'], 'db', 'aws')
p.box('s3', 1100, 560, 160, 70, 'S3: snapshots', ['Immutable model input', 'per summary + summaries'], 'storage', 'aws')
p.box('sl', 485, 925, 140, 70, 'S3: landing', ['Change files unloaded', 'from Snowflake'], 'storage', 'aws')
p.box('iq', 660, 925, 150, 70, 'SQS: ingest', ['S3 event notifications'], 'integ', 'aws')
p.box('il', 850, 925, 160, 70, 'Ingest Lambda', ['Idempotent upsert;', 'data version + 1'], 'compute', 'aws')
p.box('idq', 1050, 940, 140, 40, 'DLQ: ingest', [], 'integ', 'aws')

p.box('dp', 55, 750, 170, 60, 'CRO Data Product', ['Flag = Y claims only;', 'summary inputs only'], 'snow', 'snow')
p.box('rp', 255, 750, 170, 60, 'Handler role product', ['User, role, LOB, office,', 'assigned claims'], 'snow', 'snow')
p.box('st', 55, 840, 170, 60, 'Streams', ['Change capture on', 'both products'], 'snow', 'snow')
p.box('sm', 255, 840, 170, 60, 'Summary table', ['Writeback for reporting', 'and audit queries'], 'snow', 'snow')
p.box('tk', 55, 925, 170, 70, 'Task', ['Runs only when stream', 'has data; no business rules'], 'snow', 'snow')
p.box('ob', 255, 925, 170, 70, 'Outbox table', ['Consumes stream;', 'COPY INTO S3 stage'], 'snow', 'snow')

p.box('ae', 1340, 170, 300, 80, 'Vertex AI Agent Engine', ['ADK summary agent (single LLM agent,', 'no data-fetch tools; data passed in)'], 'gcp', 'gcp')
p.box('gm', 1340, 300, 300, 60, 'Gemini model', ['Summary generation'], 'gcp', 'gcp')
p.box('tr', 1340, 410, 300, 60, 'Cloud Trace + Cloud Logging', ['Audit trail: inputs, outputs, thought summaries'], 'gcp', 'gcp')
p.box('wf', 1340, 500, 300, 60, 'Workload Identity Federation', ['Keyless: AWS IAM role to GCP service account'], 'gcp', 'gcp')

p.edge('hd', 'sso', [(230, 265), (230, 415)], dashed=True)
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
p.edge('wk', 'ae', [(1265, 310), (1290, 310), (1290, 205), (1340, 205)])
p.edge('ae', 'gm', [(1490, 250), (1490, 300)])
p.edge('ae', 'tr', [(1640, 225), (1655, 225), (1655, 440), (1640, 440)], dashed=True)
p.edge('dp', 'st', [(140, 810), (140, 840)])
p.edge('rp', 'st', [(340, 810), (340, 825), (190, 825), (190, 840)])
p.edge('st', 'tk', [(140, 900), (140, 925)])
p.edge('tk', 'ob', [(225, 960), (255, 960)])
p.edge('ob', 'sl', [(425, 960), (485, 960)])
p.edge('sl', 'iq', [(625, 960), (660, 960)])
p.edge('iq', 'il', [(810, 960), (850, 960)])
p.edge('il', 'idq', [(1010, 960), (1050, 960)], dashed=True)
p.edge('il', 'db', [(930, 925), (930, 760), (795, 760), (795, 640)])
p.edge('s3', 'sm', [(1180, 630), (1180, 720), (450, 720), (450, 870), (425, 870)], dashed=True)

for t, x, y in [('1', 445, 240), ('2', 580, 245), ('3', 230, 340), ('4', 635, 258), ('5', 795, 258), ('6', 955, 258),
                ('7', 1115, 258), ('8', 1290, 255), ('9', 1510, 275), ('10', 1040, 520)]:
    p.badge(t, x, y)
for t, x, y in [('A', 265, 825), ('B', 455, 960), ('C', 830, 945), ('D', 930, 860), ('E', 600, 720)]:
    p.badge(t, x, y, TEAL)
p.notes(1310, 605, 360, 465, NOTES)
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
q.group('sf', 30, 540, 300, 560, 'Snowflake', 'custom', color='#29B5E8', corner='custom:snowflake')
q.group('aws', 380, 100, 900, 1010, 'AWS Cloud (LOB CloudOps account)', 'aws_cloud')
q.group('reg', 410, 140, 840, 960, 'Region us-east-1', 'region', parent='aws')
q.group('vpc', 440, 180, 790, 330, 'VPC: private subnets, 2 AZs', 'vpc', parent='reg')
q.group('gcp', 1310, 100, 360, 490, 'Google Cloud (all AI workload)', 'custom', color='#4285F4', corner='custom:gcp')
q.group('ddb', 640, 560, 440, 180, 'Amazon DynamoDB: CRO state', 'custom', parent='reg', color='#C925D1', corner='aws:dynamodb')

q.icon('sso', 100, 190, 'custom:entra', 'Azure AD', 'SSO, PKCE, PRT', 'idp')
q.icon('adg', 230, 190, 'custom:adgroup', 'AD group', 'CRO-Handlers', 'idp')
q.icon('hd', 250, 400, 'custom:person', 'Claim handler', 'HIG-joined device', 'prem')
q.icon('dx', 100, 400, 'aws:direct_connect', 'Direct Connect', 'Private link', 'prem')

q.icon('ep', 500, 250, 'aws:vpc_privatelink', 'VPC endpoint', 'execute-api', 'vpc')
q.icon('gw', 630, 250, 'aws:api_gateway', 'Private API Gateway', 'Custom domain', 'vpc')
q.icon('authz', 760, 250, 'aws:lambda', 'Lambda Authorizer', 'JWT + entitlement', 'vpc')
q.icon('al', 890, 250, 'aws:lambda', 'AWS Lambda', 'API handler', 'vpc')
q.icon('gq', 1020, 250, 'aws:sqs', 'Amazon SQS', 'Generation queue', 'vpc')
q.icon('wk', 1150, 250, 'aws:lambda', 'AWS Lambda', 'Summary worker', 'vpc')
q.icon('s3ui', 630, 400, 'aws:s3', 'Amazon S3', 'UI bundle (static)', 'vpc')
q.icon('ps', 760, 400, 'aws:systems_manager', 'Parameter Store', 'Thresholds', 'vpc')
q.icon('gd', 1020, 400, 'aws:sqs', 'Amazon SQS', 'Generation DLQ', 'vpc')
q.icon('kms', 500, 640, 'aws:key_management_service', 'AWS KMS', 'CMKs', 'reg')
q.icon('i1', 700, 630, 'custom:ddb_item', 'Current claim', 'item', 'ddb')
q.icon('i2', 800, 630, 'custom:ddb_item', 'Summary items', '(versioned)', 'ddb')
q.icon('i3', 900, 630, 'custom:ddb_item', 'Handler', 'entitlement', 'ddb')
q.icon('i4', 1000, 630, 'custom:ddb_item', 'In-flight', 'lock', 'ddb')
q.icon('s3', 1150, 800, 'aws:s3', 'Amazon S3', 'Snapshots + summaries', 'reg')
q.icon('sl', 474, 900, 'aws:s3', 'Amazon S3', 'Landing', 'reg')
q.icon('iq', 624, 900, 'aws:sqs', 'Amazon SQS', 'Ingest queue', 'reg')
q.icon('idq', 624, 1020, 'aws:sqs', 'Amazon SQS', 'Ingest DLQ', 'reg')
q.icon('il', 784, 900, 'aws:lambda', 'AWS Lambda', 'Ingest function', 'reg')
q.icon('r53', 860, 1020, 'aws:route_53', 'Route 53', 'Private hosted zone', 'reg')
q.icon('acm', 975, 1020, 'aws:certificate_manager_3', 'ACM', 'TLS certificates', 'reg')
q.icon('ct', 1090, 1020, 'aws:cloudtrail', 'CloudTrail', 'API audit', 'reg')
q.icon('cw', 1200, 1020, 'aws:cloudwatch_2', 'CloudWatch', 'Logs to Splunk', 'reg')

q.icon('dp', 100, 630, 'custom:sf_table', 'CRO Data Product', 'Flag = Y claims', 'sf')
q.icon('rp', 250, 630, 'custom:sf_table', 'Handler role product', 'User, role, claims', 'sf')
q.icon('st', 100, 760, 'custom:sf_stream', 'Streams', 'Change capture', 'sf')
q.icon('tk', 100, 900, 'custom:sf_task', 'Task', 'Unload to S3 stage', 'sf')
q.icon('sm', 250, 820, 'custom:sf_table', 'Summary table', 'Reporting writeback', 'sf')

q.icon('ae', 1400, 330, 'gcp:Vertex AI', 'Vertex AI Agent Engine', 'ADK summary agent', 'gcp')
q.icon('gm', 1580, 330, 'custom:gemini', 'Gemini', 'Model', 'gcp')
q.icon('tr', 1400, 480, 'gcp:Trace', 'Cloud Trace + Logging', 'Audit trail', 'gcp')
q.icon('wf', 1580, 480, 'gcp:Cloud IAM', 'Workload Identity', 'Federation (keyless)', 'gcp')

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
q.edge('wk', 'ddb', [(1138, 314), (1138, 620), (1080, 620)])
q.edge('wk', 'ae', [(1174, 250), (1260, 250), (1260, 330), (1376, 330)])
q.edge('ae', 'gm', [(1424, 330), (1556, 330)])
q.edge('ae', 'tr', [(1400, 394), (1400, 456)], dashed=True)
q.edge('dp', 'st', [(100, 694), (100, 736)])
q.edge('rp', 'st', [(250, 694), (250, 760), (124, 760)])
q.edge('st', 'tk', [(100, 824), (100, 876)])
q.edge('tk', 'sl', [(124, 900), (450, 900)])
q.edge('sl', 'iq', [(498, 900), (600, 900)])
q.edge('iq', 'il', [(648, 900), (760, 900)])
q.edge('iq', 'idq', [(624, 964), (624, 996)], dashed=True)
q.edge('il', 'ddb', [(784, 876), (784, 740)])
q.edge('s3', 'sm', [(1126, 800), (300, 800), (300, 820), (274, 820)], dashed=True)

for t, x, y in [('1', 380, 475), ('2', 630, 345), ('3', 175, 290), ('4', 565, 250), ('5', 695, 250), ('6', 825, 250),
                ('7', 955, 250), ('8', 1085, 250), ('9', 1490, 330), ('10', 1110, 620),
                ('A', 100, 715), ('B', 355, 900), ('C', 549, 900), ('D', 784, 808), ('E', 600, 800)]:
    q.badge(t, x, y)
q.notes(1310, 620, 360, 490, NOTES + ['Dashed line: identity, config, error or optional'])

# =====================================================================
# Page 3: handler-level access control
# =====================================================================
r = d.page('3 - Handler access control', 'CRO: Handler-Level Access Control', 1700, 820, 'conceptual')
r.panel('idp', 30, 120, 340, 200, 'Layer 1 + 2: Microsoft Entra ID', 'azure')
r.panel('snow', 30, 360, 340, 320, 'Snowflake (source of entitlements)', 'snow')
r.panel('aws', 410, 120, 870, 560, 'AWS', 'aws')

r.box('sso', 55, 170, 140, 60, 'Azure AD SSO', ['PKCE + device PRT;', 'MFA, Conditional Access'], 'security', 'idp')
r.box('adg', 215, 170, 140, 60, 'AD group', ['CRO-Handlers:', 'may use the app'], 'security', 'idp')
r.box('token', 55, 245, 300, 50, 'Access token (JWT)', ['sub, upn, groups / roles claim'], 'security', 'idp')

r.box('ui', 440, 170, 140, 70, 'CRO SPA (MSAL.js)', ['Acquires token silently;', 'handler enters claim no.'], 'ext', 'aws')
r.box('gw', 610, 170, 160, 70, 'Private API Gateway', ['Invokes authorizer on', 'every request'], 'integ', 'aws')
r.box('authz', 800, 170, 190, 70, 'Lambda Authorizer', ['L2: JWT valid + group', 'L3: may user see claim?'], 'security', 'aws')
r.box('al', 1020, 170, 150, 70, 'API Lambda', ['Runs only on Allow;', 'eligibility + summary'], 'compute', 'aws')
r.box('db', 700, 330, 300, 170, 'DynamoDB',
      ['CLAIM#<id>: eligibility, open date,', 'LOB, office, assigned adjuster', '',
       'ENT#<user>: role, LOB(s), office(s),', 'assigned claims, secured-claim access', '',
       'Two GetItems in the authorizer; cached'], 'db', 'aws')
r.box('audit', 1030, 330, 220, 110, 'Layer 4: audit log', ['user, claim, summary version,', 'decision (allow / deny), time', 'CloudWatch to Splunk; CloudTrail'], 'mgmt', 'aws')
r.box('sl', 440, 560, 150, 70, 'S3: landing', ['Role product changes', 'arrive with claim changes'], 'storage', 'aws')
r.box('iq', 620, 560, 150, 70, 'SQS: ingest', ['Same queue as', 'claim ingest'], 'integ', 'aws')
r.box('il', 800, 560, 170, 70, 'Ingest Lambda', ['Upserts ENT# items;', 'removals revoke access'], 'compute', 'aws')

r.box('dp', 55, 410, 140, 70, 'CRO Data Product', ['Claim attributes incl.', 'LOB, office, adjuster'], 'snow', 'snow')
r.box('rp', 210, 410, 150, 70, 'Handler role product', ['User, role, LOB, office,', 'assigned claims'], 'snow', 'snow')
r.box('st', 55, 505, 300, 45, 'Streams on both products', [], 'snow', 'snow')
r.box('tk', 55, 580, 300, 60, 'Task', ['Unloads changed rows to the S3 stage'], 'snow', 'snow')

r.edge('sso', 'token', [(125, 230), (125, 245)])
r.edge('adg', 'token', [(285, 230), (285, 245)])
r.edge('ui', 'sso', [(440, 190), (390, 190), (390, 158), (125, 158), (125, 170)], dashed=True)
r.edge('token', 'ui', [(355, 280), (510, 280), (510, 240)], dashed=True)
r.edge('ui', 'gw', [(580, 205), (610, 205)])
r.edge('gw', 'authz', [(770, 205), (800, 205)])
r.edge('authz', 'sso', [(895, 170), (895, 105), (45, 105), (45, 200), (55, 200)], dashed=True)
r.edge('authz', 'db', [(895, 240), (895, 330)], both=True)
r.edge('authz', 'audit', [(960, 240), (960, 300), (1100, 300), (1100, 330)], dashed=True)
r.edge('authz', 'al', [(990, 205), (1020, 205)])
r.edge('al', 'audit', [(1140, 240), (1140, 330)])
r.edge('dp', 'st', [(125, 480), (125, 505)])
r.edge('rp', 'st', [(285, 480), (285, 505)])
r.edge('st', 'tk', [(205, 550), (205, 580)])
r.edge('tk', 'sl', [(355, 610), (440, 610)])
r.edge('sl', 'iq', [(590, 595), (620, 595)])
r.edge('iq', 'il', [(770, 595), (800, 595)])
r.edge('il', 'db', [(885, 560), (885, 500)])

for t, x, y in [('1', 260, 158), ('2', 430, 280), ('3', 595, 186), ('4', 785, 186), ('5', 600, 105), ('6', 895, 285),
                ('7', 1005, 186), ('8', 1140, 285)]:
    r.badge(t, x, y)
for t, x, y in [('A', 205, 565), ('B', 397, 610), ('C', 605, 578), ('D', 885, 530)]:
    r.badge(t, x, y, TEAL)
r.notes(1310, 120, 360, 600, [
    ('h', 'FOUR LAYERS OF CONTROL'),
    'L1  Authentication: Azure AD SSO (PKCE, device PRT).',
    'L2  App access: AD group CRO-Handlers, checked in the',
    '     Lambda Authorizer before any business code runs.',
    'L3  Claim access: the same authorizer compares ENT#',
    '     for the caller with CLAIM# for the request.',
    'L4  Audit: every allow / deny decision is logged.',
    ('h', 'FLOW'),
    '1   SPA starts PKCE login; device SSO, no prompt',
    '2   Access token returned to the SPA (sub, groups)',
    '3   Every API call carries the bearer token',
    '4   Gateway invokes the Lambda Authorizer',
    '5   Signature checked against Azure AD JWKS (cached)',
    '6   Authorizer reads ENT# and CLAIM#, applies rule',
    '7   Allow: IAM policy admits the call to API Lambda',
    '8   Decision and summary version logged',
    'A   Role product changes captured like claims',
    'B-D Same ingest path; ENT# items upserted',
    ('h', 'L3 RULE (configurable, Parameter Store)'),
    'Allow when any of:',
    '  user is the assigned adjuster / supervisor',
    '  user LOB and office match the claim',
    '  user role has secured-claim access, if secured',
    'Otherwise Deny: 403, claim number not confirmed.',
    ('h', 'PATTERN NOTE'),
    'SPA_Internal_04 allows a separate Authorize API.',
    'CRO folds it into the authorizer (two reads); it can',
    'be split out later without changing the API.',
    ('h', 'FRESHNESS'),
    'Entitlements lag Snowflake by the feed latency',
    '(5 to 25 min). Removing the AD group in Entra',
    'revokes access at the next token refresh.',
])
r.legend(410, 700, 870, 90, [('flow', 'Call / data flow'), ('dashed', 'Identity / token exchange'), ('col',),
                              ('badge', '1', NAVY, 'Request path step'), ('badge', 'A', TEAL, 'Entitlement ingest step')])

# =====================================================================
# Page 4: authentication and authorization sequence
# =====================================================================
s = d.page('4 - Auth sequence', 'CRO: Authentication and API Authorization Sequence (pattern section 4)', 1700, 880, 'conceptual')
PART = [('hd', 100, 'Claim handler', 'HIG-joined device', 'ext'), ('spa', 270, 'SPA (browser)', 'MSAL.js', 'ext'),
        ('gw', 440, 'Private API Gateway', 'VPC endpoint', 'integ'), ('s3', 610, 'S3: UI bundle', 'static', 'storage'),
        ('aad', 780, 'Azure AD', 'Entra ID', 'security'), ('az', 950, 'Lambda Authorizer', 'L2 + L3', 'security'),
        ('db', 1120, 'DynamoDB', 'ENT#, CLAIM#, state', 'db'), ('al', 1290, 'API Lambda', 'summary API', 'compute')]
X = {}
for i, x, t, sub, k in PART:
    X[i] = x
    s.box(i, x - 70, 130, 140, 50, t, [sub], k)
    s.box(i + '_l', x - 1, 180, 2, 640, '', [], 'mgmt')
MSG = [(210, 'hd', 'spa', 0, '1'), (240, 'spa', 'gw', 0, '2'), (270, 'gw', 's3', 0, '3'), (300, 's3', 'spa', 1, ''),
       (340, 'spa', 'aad', 0, '4'), (370, 'aad', 'spa', 1, '5'),
       (410, 'spa', 'gw', 0, '6'), (440, 'gw', 'az', 0, '7'), (470, 'az', 'aad', 1, '7a'), (500, 'az', 'db', 0, '7b'),
       (530, 'db', 'az', 1, ''), (560, 'az', 'gw', 1, '7c'), (590, 'gw', 'spa', 1, '8'),
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
    '7b  ENT#<user> and CLAIM#<id> read',
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
# Page 5: pattern conformance
# =====================================================================
c = d.page('5 - Pattern conformance', 'CRO vs HIG Pattern SPA_Internal_04 v1: Conformance and Declared Deviations', 1700, 860, 'conceptual')
c.notes(30, 120, 400, 710, [
    ('h', 'ADOPTED AS WRITTEN'),
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
    'D2  Fine-grained authorization performed inside the Lambda Authorizer',
    '    instead of a separate Authorize API.',
    '    Why: the pattern calls the Authorize API "when needed". CRO\'s rule is',
    '    two DynamoDB reads (ENT# for the user, CLAIM# for the claim). A second',
    '    service adds a network hop, a failure point and a deployment with no',
    '    added control. The authorizer still returns the scoped IAM policy the',
    '    pattern requires. Reversible: split into an Authorize API if the rule',
    '    set grows (hierarchies, exceptions) with no change to callers.',
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
    '  Cloud Trace, WIF',
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
    '6  Role product columns',
    '   available in Snowflake',
    '   (LOB, office, adjuster,',
    '   secured-claim access)',
    '7  Whether all CRO-Handlers',
    '   may read all flagged',
    '   claims (collapses L3)',
    ('h', 'ASSUMPTIONS'),
    'Pilot: one LOB or office',
    'Handlers already in Azure',
    '  AD; group created by IAM',
    'Direct Connect and VPC',
    '  endpoints exist in the',
    '  LOB account (landing zone)',
])

base = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/CRO_Architecture_v0.4'
d.save(base)
