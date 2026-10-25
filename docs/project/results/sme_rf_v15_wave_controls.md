# v15 fixed-cell wave/control results

Recorded 2026-10-23. Source: `outputs/output-10231150.pdf`; PDF pp.1-12 / printed pp.60-71.
SHA256: `06bf2bc0212a3b8d19b59e9f6607bf6ceb29d47c166a0dd0efd70dec89f9e8cc`.

All pages visually inspected. Numeric tables below transcribe aggregate platform output, not microdata.
User identifies the latest platform run; administrator real-data versus online simulation provenance remains unconfirmed.
PASS; 66 fits, 15/15 balance checks, 5 projections, 0 variation fallbacks; no model/design issues.
Fixed 10/3/3 cells; W4 omits 2024q3. M0 cell FE; M1 adds 3 linear portfolio terms; M2 adds 6 polynomial terms.
Gain units: 10,000 yuan. User-cluster SE. Same outcome-specific sample across M0/M1/M2.
CPI/cost and other percentage-bin outcomes use percentage-point midpoints; stock uses index points; local environment uses -1/0/1.
NAV screen False; nav_price_annotated_v1; post-window responses; complete coverage and 12-month history.

## Common samples (printed p.62)

|Outcome|W5 N|W5 positive|W5 recorded zero|W5 absent zero|W4 N|W4 positive|W4 recorded zero|W4 absent zero|q3 removed|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|stock|5349|3171|210|1968|3586|2083|147|1356|1763|
|gdp|8258|4617|296|3345|6280|3505|225|2550|1978|
|cpi|9016|5084|312|3620|6863|3850|242|2771|2153|
|house|6724|3703|248|2773|4632|2526|174|1932|2092|
|rate|7516|4161|280|3075|5251|2872|205|2174|2265|
|env_local|13288|7229|435|5624|10102|5471|336|4295|3186|
|rev|22018|11959|736|9323|17250|9252|580|7418|4768|
|market|21375|11621|723|9031|16744|8984|566|7194|4631|
|price|9901|5476|328|4097|7381|4064|246|3071|2520|
|wage|10789|5936|354|4499|8150|4460|272|3418|2639|
|input_cost|10328|5659|353|4316|7763|4233|272|3258|2565|

Stock has four actual waves in W5 and three in W4 because 2024q2 stock expectations are unavailable.
Counts are observation counts, not necessarily unique users. Zero cells do not supply direct within-cell gain variation.

## W5 estimates (printed p.64)

|Outcome|M0 beta|M0 SE|M0 raw p|M1 beta|M1 SE|M1 raw p|M2 beta|M2 SE|M2 raw p|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|stock|-11.544435|46.939729|0.805727|-18.022320|48.762448|0.711685|-1.618427|46.101837|0.971996|
|gdp|0.106363|0.250795|0.671489|0.125770|0.255432|0.622451|0.072728|0.244512|0.766131|
|cpi|0.448024|0.163768|0.006224|0.454813|0.160083|0.004496|0.444359|0.159621|0.005372|
|house|-1.042896|1.930167|0.588981|-0.998231|1.953663|0.609384|-0.771953|1.985571|0.697438|
|rate|0.055465|0.103944|0.593613|0.058374|0.103730|0.573607|0.040798|0.106296|0.701116|
|env_local|0.079706|0.064134|0.213943|0.082909|0.062312|0.183338|0.080515|0.062821|0.199961|
|rev|0.043365|0.422784|0.918304|0.080242|0.419146|0.848179|0.080814|0.420391|0.847557|
|market|-0.446843|0.491985|0.363749|-0.412819|0.487246|0.396856|-0.429954|0.492298|0.382466|
|price|-0.332506|0.256984|0.195706|-0.272961|0.260339|0.294418|-0.322317|0.259767|0.214681|
|wage|-0.288068|0.181400|0.112281|-0.274988|0.180012|0.126608|-0.299997|0.181438|0.098242|
|input_cost|-0.422761|0.195679|0.030736|-0.434509|0.195211|0.026025|-0.495144|0.183181|0.006871|

## W4 estimates (printed p.66)

|Outcome|M0 beta|M0 SE|M0 raw p|M1 beta|M1 SE|M1 raw p|M2 beta|M2 SE|M2 raw p|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|stock|39.331722|55.705879|0.480151|36.904204|61.892443|0.550999|107.470637|69.403786|0.121506|
|gdp|0.093090|0.234521|0.691415|0.052355|0.248249|0.832968|-0.083745|0.240307|0.727470|
|cpi|0.313729|0.163268|0.054662|0.333208|0.157342|0.034198|0.326632|0.160848|0.042286|
|house|0.037300|2.068412|0.985612|0.408247|2.123753|0.847563|0.527544|2.244485|0.814178|
|rate|-0.045699|0.133766|0.732627|-0.040539|0.140671|0.773208|-0.075380|0.160068|0.637692|
|env_local|0.065285|0.079826|0.413447|0.086738|0.076655|0.257829|0.080612|0.077390|0.297576|
|rev|0.135159|0.577319|0.814895|0.369335|0.576220|0.521547|0.272189|0.587871|0.643358|
|market|-0.111568|0.657896|0.865339|0.109803|0.660892|0.868044|0.103864|0.685118|0.879502|
|price|-0.211774|0.277441|0.445277|0.066148|0.277034|0.811282|-0.053948|0.310841|0.862215|
|wage|-0.136371|0.149259|0.360899|-0.047252|0.144870|0.744294|-0.143223|0.148781|0.335728|
|input_cost|-0.190027|0.156606|0.224974|-0.181232|0.166683|0.276911|-0.308408|0.139668|0.027234|

## Signed positive BASE balance (printed pp.68-69)

std/CI use common five-wave positive BASE SD(gain)/SD(target), not within-wave normalization or partial correlation.
log = log portfolio size; poly00 = squared standardized log size; poly02 = standardized log size times historical mean.
All are cell-FE-only checks. Eight zero-p target assignments are not directly recoverable from deduplicated wave/p/note panels.
A dash in p below records that reporting limitation, not an unperformed test. Exact zero is never inferred.

|Wave|Target|N|Raw beta|std|CI low|CI high|Printed p, where matched|
|---|---|---:|---:|---:|---:|---:|---:|
|2024q2|log|3861|-0.096026|-0.004777|-0.031739|0.022185|0.728403|
|2024q2|poly00|3861|-0.088070|-0.018717|-0.131945|0.094511|0.745942|
|2024q2|poly02|3861|-0.076706|-0.014365|-0.084340|0.055610|0.687411|
|2024q3|log|3304|-0.920871|-0.045809|-0.051895|-0.039722|-|
|2024q3|poly00|3304|-0.830514|-0.176504|-0.197695|-0.155313|-|
|2024q3|poly02|3304|0.468884|0.087811|0.050506|0.125117|0.000004|
|2024q4|log|2945|1.642355|0.081699|0.065452|0.097946|-|
|2024q4|poly00|2945|1.559731|0.331479|0.270493|0.392466|-|
|2024q4|poly02|2945|0.363406|0.068058|0.003655|0.132460|0.038336|
|2025q1|log|2046|0.563525|0.028033|0.017760|0.038305|-|
|2025q1|poly00|2046|0.526958|0.111991|0.072382|0.151600|-|
|2025q1|poly02|2046|0.321349|0.060181|0.017652|0.102711|0.005546|
|2025q2|log|2275|1.190618|0.059227|0.046039|0.072416|-|
|2025q2|poly00|2275|1.092512|0.232184|0.182713|0.281655|-|
|2025q2|poly02|2275|-0.237226|-0.044427|-0.134058|0.045204|0.331297|

All CIs were checked for midpoint agreement; positive BASE counts sum to 14,431 (11,127 without q3).

## Derived uncertainty supplement (not printed platform values)

CIs = printed beta +/- 1.96 times printed SE. Holm uses the 11 rounded p values separately within each wave/model.
These approximate values do not adjust across specifications or historical specification searches.

|Wave|Outcome|Model|Approx. CI low|Approx. CI high|Approx. Holm p|
|---|---|---|---:|---:|---:|
|W5|stock|M0|-103.546304|80.457434|1.000000|
|W5|stock|M1|-113.596718|77.552078|1.000000|
|W5|stock|M2|-91.978028|88.741174|1.000000|
|W5|gdp|M0|-0.385195|0.597921|1.000000|
|W5|gdp|M1|-0.374877|0.626417|1.000000|
|W5|gdp|M2|-0.406516|0.551972|1.000000|
|W5|cpi|M0|0.127039|0.769009|0.068464|
|W5|cpi|M1|0.141050|0.768576|0.049456|
|W5|cpi|M2|0.131502|0.757216|0.059092|
|W5|house|M0|-4.826023|2.740231|1.000000|
|W5|house|M1|-4.827410|2.830948|1.000000|
|W5|house|M2|-4.663672|3.119766|1.000000|
|W5|rate|M0|-0.148265|0.259195|1.000000|
|W5|rate|M1|-0.144937|0.261685|1.000000|
|W5|rate|M2|-0.167542|0.249138|1.000000|
|W5|env_local|M0|-0.045997|0.205409|1.000000|
|W5|env_local|M1|-0.039223|0.205041|1.000000|
|W5|env_local|M2|-0.042614|0.203644|1.000000|
|W5|rev|M0|-0.785292|0.872022|1.000000|
|W5|rev|M1|-0.741284|0.901768|1.000000|
|W5|rev|M2|-0.743152|0.904780|1.000000|
|W5|market|M0|-1.411134|0.517448|1.000000|
|W5|market|M1|-1.367821|0.542183|1.000000|
|W5|market|M2|-1.394858|0.534950|1.000000|
|W5|price|M0|-0.836195|0.171183|1.000000|
|W5|price|M1|-0.783225|0.237303|1.000000|
|W5|price|M2|-0.831460|0.186826|1.000000|
|W5|wage|M0|-0.643612|0.067476|1.000000|
|W5|wage|M1|-0.627812|0.077836|1.000000|
|W5|wage|M2|-0.655615|0.055621|0.884178|
|W5|input_cost|M0|-0.806292|-0.039230|0.307360|
|W5|input_cost|M1|-0.817123|-0.051895|0.260250|
|W5|input_cost|M2|-0.854179|-0.136109|0.068710|
|W4|stock|M0|-69.851801|148.515245|1.000000|
|W4|stock|M1|-84.404984|158.213392|1.000000|
|W4|stock|M2|-28.560784|243.502058|1.000000|
|W4|gdp|M0|-0.366571|0.552751|1.000000|
|W4|gdp|M1|-0.434213|0.538923|1.000000|
|W4|gdp|M2|-0.554747|0.387257|1.000000|
|W4|cpi|M0|-0.006276|0.633734|0.601282|
|W4|cpi|M1|0.024818|0.641598|0.376178|
|W4|cpi|M2|0.011370|0.641894|0.422860|
|W4|house|M0|-4.016788|4.091388|1.000000|
|W4|house|M1|-3.754309|4.570803|1.000000|
|W4|house|M2|-3.871647|4.926735|1.000000|
|W4|rate|M0|-0.307880|0.216482|1.000000|
|W4|rate|M1|-0.316254|0.235176|1.000000|
|W4|rate|M2|-0.389113|0.238353|1.000000|
|W4|env_local|M0|-0.091174|0.221744|1.000000|
|W4|env_local|M1|-0.063506|0.236982|1.000000|
|W4|env_local|M2|-0.071072|0.232296|1.000000|
|W4|rev|M0|-0.996386|1.266704|1.000000|
|W4|rev|M1|-0.760056|1.498726|1.000000|
|W4|rev|M2|-0.880038|1.424416|1.000000|
|W4|market|M0|-1.401044|1.177908|1.000000|
|W4|market|M1|-1.185545|1.405151|1.000000|
|W4|market|M2|-1.238967|1.446695|1.000000|
|W4|price|M0|-0.755558|0.332010|1.000000|
|W4|price|M1|-0.476839|0.609135|1.000000|
|W4|price|M2|-0.663196|0.555300|1.000000|
|W4|wage|M0|-0.428919|0.156177|1.000000|
|W4|wage|M1|-0.331197|0.236693|1.000000|
|W4|wage|M2|-0.434834|0.148388|1.000000|
|W4|input_cost|M0|-0.496975|0.116921|1.000000|
|W4|input_cost|M1|-0.507931|0.145467|1.000000|
|W4|input_cost|M2|-0.582157|-0.034659|0.299574|

## Source calendar (printed p.61)

|Wave|Fund rows|Start|End|n_starts|n_ends|Gate|
|---|---:|---|---|---:|---:|---|
|2024q2|23020|2024-06-01|2024-06-13|1|1|PASS|
|2024q3|23686|2024-09-01|2024-09-17|1|1|PASS|
|2024q4|24391|2024-12-01|2024-12-10|1|1|PASS|
|2025q1|25217|2025-03-01|2025-03-17|1|1|PASS|
|2025q2|26045|2025-06-01|2025-06-12|1|1|PASS|

Addon policy: per_question_unique_mapped_answer; missing plus unique valid retains valid;
conflicting/unknown answer makes that question missing; missing submit ID excluded from addon merge;
resolved keys/values PASS; small-group details not output.

## Timing and validation (printed p.70)

|Stage|Seconds|
|---|---:|
|setup|0.01|
|read|181.91|
|survey|4.20|
|aggregate|508.17|
|sample|5.50|
|models|146.08|

Stage sum 845.87 seconds (14.10 minutes), not separately measured wall time.
Regression/variation component 136.28 seconds; balance .75 seconds. These overlap stages.
Checked all sample partition/difference identities and 66 normal-p identities to rounding.
The report omits full-mode uncertainty/preparation appendices by design.
See [findings](../findings.md) for interpretation and [run log](../run-log.md) for provenance.
