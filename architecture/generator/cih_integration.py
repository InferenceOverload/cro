#!/usr/bin/env python3
"""CRO <-> Claims Insights Hub integration one-pager. CRO shown as a black box; no internals."""
import os, sys
sys.path.insert(0, os.environ.get('ARCHDIAGRAM_SCRIPTS', '/mnt/skills/plugins/cloud-architecture-diagrams/scripts'))
from archdiagram import Diagram, CUSTOM

W = 'stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"'
CUSTOM['apigee'] = ('<rect x="0" y="0" width="48" height="48" rx="6" fill="#4285F4"/>'
                    f'<circle cx="24" cy="22" r="9" {W}/><path d="M24,13 V31 M15,22 H33 M18,16 Q24,22 30,28 M30,16 Q24,22 18,28" {W}/>'
                    '<text x="24" y="44" text-anchor="middle" font-size="7.5" font-family="Arial" font-weight="bold" fill="#fff">APIGEE</text>')

d = Diagram(subtitle='The Hartford EDS Claims  |  Integration proposal for CIO / Claims Insights Hub  |  v0.2  |  2026-11-06')
p = d.page('CIH integration', 'CRO Claim Summary API: Integration with Claims Insights Hub', 1700, 930, 'conceptual')
NAVY = '#1F4E79'

p.panel('cio', 30, 120, 560, 330, 'CIO-owned (Claims Insights Hub and mediation)', 'neutral')
p.panel('eds', 640, 120, 640, 330, 'EDS Claims-owned (CRO service)', 'aws')
p.panel('ctr', 30, 480, 1250, 425, 'Integration contract (what CIH needs to know)', 'neutral')

p.box('hd', 60, 175, 180, 60, 'Claim handler', ['Signed in to CIH;', 'CIH owns the screen'], 'ext', 'cio')
p.box('cih', 60, 270, 180, 80, 'Claims Insights Hub', ['Renders the summary;', 'enforces which claims', 'a handler may see'], 'ext', 'cio')
p.box('med', 300, 270, 260, 80, 'Mediation layer (CIO AWS)', ['Registered Apigee consumer:', 'API key + client certificate (mTLS);', 'routes, retries, caches if desired'], 'integ', 'cio')
p.box('apic', 680, 270, 200, 80, 'Apigee', ['CRO Summary API product;', 'subscription, quota, rate', 'limit, mTLS termination'], 'integ', 'eds')
p.box('cro', 920, 175, 330, 230, 'CRO Summary Service',
      ['Authenticates the calling service;', 'returns summaries for flagged claims', 'older than 30 days;', 'regenerates only when the claim', 'has changed since the last summary;', 'every summary versioned and auditable;', 'AI generation on Vertex AI Agent Engine', '(traced for audit and compliance)'], 'compute', 'eds')
p.box('ui', 680, 175, 200, 60, 'CRO UI (interim)', ['EDS handler screen until', 'CIH hosts the summary'], 'ext', 'eds')

p.edge('hd', 'cih', [(150, 235), (150, 270)])
p.edge('cih', 'med', [(240, 310), (300, 310)])
p.edge('med', 'apic', [(560, 310), (680, 310)])
p.edge('apic', 'cro', [(880, 310), (920, 310)])
p.edge('ui', 'cro', [(880, 205), (920, 205)])
p.edge('cro', 'apic', [(920, 330), (880, 330)], dashed=True)
p.edge('apic', 'med', [(680, 330), (560, 330)], dashed=True)
p.edge('med', 'cih', [(300, 330), (240, 330)], dashed=True)

for t, x, y in [('1', 150, 252), ('2', 270, 296), ('3', 620, 296), ('4', 900, 296), ('5', 620, 346)]:
    p.badge(t, x, y)

p.notes(50, 515, 400, 375, [
    ('h', 'ENDPOINTS (v1, OpenAPI published)'),
    'GET  /claims/{claimId}/summary',
    '      latest summary, or 202 if generating',
    'GET  /claims/{claimId}/summary/versions',
    'GET  /claims/{claimId}/summary/{version}',
    'POST /claims/{claimId}/summary',
    '      request (re)generation; 202 + job ref',
    ('h', 'RESPONSES'),
    '200  summary payload',
    '202  generation in progress; poll GET',
    '404  claim not flagged / not eligible',
    '401 / 403  caller not authorized',
    '429  quota exceeded (Apigee)',
    ('h', 'PAYLOAD'),
    'summaryText, version, generatedAt,',
    'dataAsOf, claimDataVersion, stale (bool),',
    'promptVersion, modelVersion, traceId',
])
p.notes(470, 515, 400, 375, [
    ('h', 'AUTHENTICATION AND AUTHORIZATION'),
    'Caller: mediation layer service identity',
    '  Apigee API key + mTLS client certificate',
    '  (same front door as other EDS services)',
    'No handler token crosses to CRO',
    'CRO policy for this caller: read + request',
    '  generation only; no admin methods',
    ('h', 'HANDLER-LEVEL VISIBILITY'),
    'Not applied in CRO (business scope: all',
    '  CRO-Handlers, all flagged claims). If CIH',
    '  needs claim-level rules, CIH enforces them.',
    'Optional: mediation passes X-Handler-Id',
    '  for CRO audit logging only.',
    ('h', 'AUDIT'),
    'Every call logged: caller, claim, version,',
    '  outcome, time; CloudWatch to Splunk.',
    'Model inputs, outputs and traces retained',
    '  on the EDS side for compliance review.',
])
p.notes(890, 515, 370, 375, [
    ('h', 'FLOW'),
    '1  Handler opens a claim in CIH',
    '2  CIH asks mediation for the summary',
    '3  Mediation calls the Apigee product',
    '4  Apigee forwards to CRO; 200 or 202',
    '5  Response back via mediation to CIH',
    ('h', 'NON-FUNCTIONAL'),
    'Latency (targets, to validate): stored',
    '  < 500 ms p95; generation 30 to 90 s',
    'Volume: on demand only; no bulk pull',
    'Availability: tied to CRO metal tier',
    ('h', 'ONBOARDING STEPS'),
    'a  EDS publishes product + OpenAPI',
    'b  CIO subscribes mediation in Apigee',
    'c  Certificates exchanged; test in non-prod',
    'd  CIH integrates; interim CRO UI retired',
    ('h', 'OPEN QUESTIONS FOR CIO'),
    'Pull on demand (this) or push on ready?',
    'Does mediation carry handler identity?',
    'Target PI for CIH to consume the API?',
])

base = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/CRO_CIH_Integration'
d.save(base)
