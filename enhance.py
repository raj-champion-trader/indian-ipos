#!/usr/bin/env python3
"""Patch analysis/companies.csv with AI/moat/growth notes per ticker, then rebuild md.

Usage: python3 enhance.py
Append entries to NOTES per batch. Existing values are overwritten only if non-empty here.
"""
import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "analysis" / "companies.csv"
NEW_COLS = ["AI_Moat", "RevGrowthCeiling", "GrowthCatalysts", "StagnationCatalysts"]

NOTES = {
    # ---------------- Batch A ----------------
    "AEROFLEX": {
        "AI_Moat": "AI a tailwind not threat: data-centre buildout drives liquid-cooling skid demand. Moat = process engineering certs + export OEM relationships; hard to codify, durable.",
        "RevGrowthCeiling": "Core hose business caps at global niche market share (low-double-digit); SFN cooling skids ride DC capex cycle - ceiling high until AI buildout peaks.",
        "GrowthCatalysts": "SFN data-centre cooling order ramp; export share gains; new metal bellings line.",
        "StagnationCatalysts": "Steel input cost spikes; DC capex cycle pause; export customer concentration.",
    },
    "ATHERENERG": {
        "AI_Moat": "Software/OTA + charging data give mild ecosystem moat; AI battery analytics helps. But AI cannot stop hardware commoditisation vs TVS/Bajaj scale - moat rests on brand + network, AI marginal.",
        "RevGrowthCeiling": "India 2W EV segment; realistic mid-single-digit share = Rs 8-15k cr revenue ceiling long-term; needs new segments (3W, exports) to break it.",
        "GrowthCatalysts": "Rizta family volume; distribution expansion; falling cell costs aiding margin per scooter; charging network lock-in.",
        "StagnationCatalysts": "Price war with incumbent OEMs; subsidy cuts; cash burn if volumes lag; cell import dependency.",
    },
    "AVALON": {
        "AI_Moat": "AI server/networking demand lifts EMS volumes - tailwind. Moat thin (contract manufacturing) but qualification lock-ins and China+1/PLI shift preserve it.",
        "RevGrowthCeiling": "Order book Rs 3,200 cr (~1.5x revenue) gives near-term visibility; India EMS TAM growing 25%+ keeps ceiling distant.",
        "GrowthCatalysts": "Defence/aerospace order ramp; AI-hardware assemblies; new plant utilisation.",
        "StagnationCatalysts": "Component import dependence; customer concentration; margin squeeze as peers scale.",
    },
    "ACMESOLAR": {
        "AI_Moat": "AI = structural power-demand driver (data centres); grid firming needs make BESS valuable. Moat = land bank + PPA portfolio, AI-proof.",
        "RevGrowthCeiling": "Bounded by PPA wins and debt capacity; 500 GW national target = long runway; growth 20-30% then plateau at portfolio maturity.",
        "GrowthCatalysts": "Capacity commissioning; BESS tariff awards; merchant power upside; falling module prices.",
        "StagnationCatalysts": "Reverse-auction tariff competition; curtailment; interest cost on project debt; PPA counterparty stress.",
    },
    "AZAD": {
        "AI_Moat": "Zero-defect qualification moat with global OEMs (multi-year vendor lock) - AI cannot displace certified precision machining; AI-era aerospace demand rising. Moat durable.",
        "RevGrowthCeiling": "Order book ~Rs 6,000 cr (~10x revenue) = multi-year ramp before ceiling binds; global precision parts TAM large.",
        "GrowthCatalysts": "A&D share ramp; gas turbine/nuclear demand; design-led workshare increase.",
        "StagnationCatalysts": "OEM program delays; super-alloy cost inflation; export geopolitics.",
    },
    "ATLANTAELE": {
        "AI_Moat": "AI/grid buildout = global transformer supercycle demand. Moat = MVA-rating qualifications + utility relationships; AI zero threat to product, huge demand driver.",
        "RevGrowthCeiling": "Capacity-bound near term; ceiling = installed capacity x utilisation; expansion pace defines growth cap.",
        "GrowthCatalysts": "Utility ordering cycle; renewables grid-connection demand; export openings amid global shortage.",
        "StagnationCatalysts": "CRGO/copper costs; government tender pauses; competition from Siemens/BHEL scale.",
    },
    "AMANTA": {
        "AI_Moat": "Moat = sterile-manufacturing approvals and compliance record; AI irrelevant to moat, marginal QC efficiency gain.",
        "RevGrowthCeiling": "India ophthalmic/IV market ~10% grower; ceiling moderate unless CMO scales.",
        "GrowthCatalysts": "Ophthalmic brand build; CMO contract wins; post-IPO capacity.",
        "StagnationCatalysts": "Price control (NLEM); tender competition; API/packaging costs.",
    },
    "AKUMS": {
        "AI_Moat": "AI neutral for formulation CDMO; moat = capacity scale + regulatory track record, but thin pricing power. AI drug discovery upstream may shift client mix, not volumes.",
        "RevGrowthCeiling": "Already India's largest by volume; growth = volume + premiumisation into niche formats; ceiling moderate-high within ~$15-20bn India CDMO pool.",
        "GrowthCatalysts": "New capacity; MNC CDMO wins; gummies/nutraceutical diversification.",
        "StagnationCatalysts": "Customer concentration (top 10% = 47% of revenue); pricing pressure; working-capital strain (101 inventory days).",
    },
    "AEGISVOPAK": {
        "AI_Moat": "Physical irreplaceable assets (port tank farms + licences) = AI-proof moat.",
        "RevGrowthCeiling": "Bounded by tank capacity and India LPG/chemical import growth; steady 8-12%; step-change only via capex.",
        "GrowthCatalysts": "New tank capacity; LPG import volume growth; chemical-hub demand; debt paydown lifting PAT.",
        "StagnationCatalysts": "Import policy shifts; competing terminals; interest on Rs 3,731 cr debt.",
    },
    "ABDL": {
        "AI_Moat": "Brand + distribution moat (Officer's Choice) AI-proof; AI neutral.",
        "RevGrowthCeiling": "Value whisky grows with population/income ~5-8%; premiumisation lifts realisations; ceiling moderate.",
        "GrowthCatalysts": "Premiumisation (ICONiQ); state distribution expansion; price hikes in key states.",
        "StagnationCatalysts": "Excise policy shocks; ENA/grain/packaging costs; prohibition risk in select states; premium competition from United Spirits.",
    },
    "ASKAUTOLTD": {
        "AI_Moat": "Safety-part supplier qualification + ~50% 2W braking share = durable vs AI; real threat is EV shift (regen braking cuts friction brake content).",
        "RevGrowthCeiling": "Tied to India 2W volumes (~5% CAGR); ceiling low-moderate; EV transition caps long-term brake content per vehicle.",
        "GrowthCatalysts": "2W volume recovery; exports; higher-value advanced braking content.",
        "StagnationCatalysts": "EV penetration; steel/aluminium cost; OEM annual pricing cuts.",
    },
    "AHCL": {
        "AI_Moat": "Moat = CDMO chemistry relationships with 2 global innovators - fragile concentration; AI compresses molecule dev timelines, mild competitive threat.",
        "RevGrowthCeiling": "Niche intermediates; 393 inventory days caps scalability; ceiling low-moderate pending CDMO commercial supplies.",
        "GrowthCatalysts": "CDMO commercialisation from Q3 FY27; API volume growth (+43% FY26); capacity utilisation.",
        "StagnationCatalysts": "Cash trapped in 220 debtor days; two-client concentration; price erosion.",
    },
    "AFIL": {
        "AI_Moat": "Moat = branch-level underwriting of unbanked rural borrowers; AI credit-scoring fintechs are a medium-term threat, though segment too small/touch-heavy for them today.",
        "RevGrowthCeiling": "Rural vehicle-finance niche, small book; ceiling moderate.",
        "GrowthCatalysts": "MSME/LAP book expansion; vehicle finance recovery; branch adds.",
        "StagnationCatalysts": "Rural credit cycles; funding cost; fintech/NBFC competition compressing yields.",
    },
    "ARIS": {
        "AI_Moat": "Aggregation platform moat thin - matching commoditised by AI procurement tools; defensible part = credit extension + logistics. AI mild threat, own AI tools partial offset.",
        "RevGrowthCeiling": "India construction-materials spend in lakh crores - revenue ceiling far; 9% OPM caps profit not revenue.",
        "GrowthCatalysts": "City expansion; SKU/category adds; credit solutions attach; operating leverage.",
        "StagnationCatalysts": "Real estate slowdown; working-capital bloat; credit losses on developer receivables.",
    },
    "ANTHEM": {
        "AI_Moat": "AI-accelerated molecule design feeds CDMO pipeline - net tailwind. Moat = integrated chemistry+biology platforms (RNAi, ADC, peptides) sticky with global pharma.",
        "RevGrowthCeiling": "Global CRAM shift to India structural; ceiling high.",
        "GrowthCatalysts": "Long-term CDMO contracts; biologics capacity ramp; specialty ingredients pricing.",
        "StagnationCatalysts": "Global pharma capex cycles; biosecurity/geopolitics; pricing pressure.",
    },
    "ARKADE": {
        "AI_Moat": "Moat = Mumbai land/JDA relationships + approval track record; AI irrelevant.",
        "RevGrowthCeiling": "Project-execution bound; guided pipeline implies Rs 1,500-2,500 cr plateau unless redevelopment flow deepens.",
        "GrowthCatalysts": "Redevelopment deal flow; launches; Mumbai price appreciation; near debt-free balance sheet.",
        "StagnationCatalysts": "Approval delays; Mumbai property downturn; single-city concentration.",
    },
    "AADHARHFC": {
        "AI_Moat": "Moat = informal-income underwriting skill + low-ticket cost-to-serve; bigtech AI scoring a long-term threat but segment too granular for them near-term.",
        "RevGrowthCeiling": "Affordable housing credit gap huge; book can compound ~20% for years before ceiling binds.",
        "GrowthCatalysts": "Geographic expansion; LTV-disciplined book growth; securitisation funding access.",
        "StagnationCatalysts": "Credit events in informal-income belts; funding-cost spikes; Aavas/Home First competition.",
    },
    "AJAXENGG": {
        "AI_Moat": "Moat = dealer network + service reach in niche equipment; AI neutral; automation/3D-printing trend mild tailwind for advanced solutions.",
        "RevGrowthCeiling": "Tied to India infra/housing capex cycle; equipment market cyclical; ceiling moderate.",
        "GrowthCatalysts": "Infra capex cycle; exports; 3D concrete printing adoption.",
        "StagnationCatalysts": "Infra spend pauses; receivables bloat (161 days); Schwing Stetter competition.",
    },
    "AGARWALEYE": {
        "AI_Moat": "Surgical/brand/surgeon-network moat intact; AI diagnostics a screening feeder (tailwind) not a surgery substitute. AI net positive if adopted early.",
        "RevGrowthCeiling": "Organised eye-care penetration in tier-2/3 low; ceiling high via hospital roll-out.",
        "GrowthCatalysts": "New-hospital maturation; cataract/refractive volume; tier-2/3 expansion; medical value travel.",
        "StagnationCatalysts": "Surgeon attrition; capex/debt drag (Rs 1,066 cr borrowings); pricing competition from regional chains.",
    },
    "AFCONS": {
        "AI_Moat": "Moat = specialised execution skill (marine, tunnels, metros) built over decades; AI project-management tools marginal gain, no displacement risk.",
        "RevGrowthCeiling": "India infra pipeline Rs 100+ lakh cr; ceiling distant; revenue tracks order-book wins.",
        "GrowthCatalysts": "Marine/tunnel niche awards; metro build-out; ~Rs 40,000 cr order book execution.",
        "StagnationCatalysts": "Government receivable delays (105 debtor days); bitumen/steel costs; aggressive bidding margin dilution.",
    },
    "ADVANCE": {
        "AI_Moat": "Moat = distributor network + registrations; AI agri-advisory shifts brand dynamics mildly; precision agriculture reducing pesticide volumes is the real long-term threat.",
        "RevGrowthCeiling": "India agrochem ~Rs 60-70k cr growing 6-8%; ceiling moderate.",
        "GrowthCatalysts": "New technicals capacity; export registrations; brand portfolio expansion.",
        "StagnationCatalysts": "Monsoon failure; Chinese price competition; pesticide bans; biopesticide/GMO substitution.",
    },
    "ARSSBL": {
        "AI_Moat": "AI robo-advisory + discount brokers compress take rates - real threat; moat = advisory relationships + margin book. AI adoption own-side needed to defend.",
        "RevGrowthCeiling": "Revenue pool tied to market volumes/cycles; demat growth maturing; ceiling moderate.",
        "GrowthCatalysts": "Margin-trading (MTF) book expansion; distribution AUM build; HNI institutional mix.",
        "StagnationCatalysts": "F&O regulatory crackdowns; bear-market volume dry-up; fee compression.",
    },
    "ALLTIME": {
        "AI_Moat": "White-label manufacturing moat thin (relationships + cost); AI low threat but also low protection - customers can switch suppliers.",
        "RevGrowthCeiling": "Global houseware demand steady low-single-digit; ceiling low-moderate.",
        "GrowthCatalysts": "New retailer wins; capacity; product-range extension.",
        "StagnationCatalysts": "Polymer costs; retailer destocking; tariffs; China/Vietnam cost competition.",
    },
    "AWFIS": {
        "AI_Moat": "AI-era hybrid/distributed work = structural flex-demand driver. Moat = location portfolio + enterprise contracts; AI net positive.",
        "RevGrowthCeiling": "India flex workspace ~55-65 mn sq ft growing double-digit; ceiling moderate-high.",
        "GrowthCatalysts": "Seat occupancy fill; enterprise take-ups; managed-seats asset-light aggregation.",
        "StagnationCatalysts": "IT-sector hiring freeze; long lease commitments vs demand shocks; IndiQube/WeWork price competition.",
    },
    "AASTHA": {
        "AI_Moat": "Commodity yarn converter - minimal moat; AI irrelevant.",
        "RevGrowthCeiling": "Yarn demand tied to garment exports; ceiling low.",
        "GrowthCatalysts": "Capacity utilisation; cotton spread management; export recovery.",
        "StagnationCatalysts": "Cotton price volatility; power costs; Bangladesh/China competition.",
    },
    "AEQUS": {
        "AI_Moat": "OEM qualification lock-in within integrated SEZ ecosystem - durable; AI-era aerospace demand rising. Moat preserved.",
        "RevGrowthCeiling": "Global aero supply chain shifting to India; ceiling high; consumer vertical diversifies cycle.",
        "GrowthCatalysts": "A&D order ramp; post-IPO deleveraging; assembly/surface-treatment workshare gains.",
        "StagnationCatalysts": "OEM rate cuts; ramp-up cost drag; SEZ policy changes.",
    },
    "AEROPLANE": {
        "AI_Moat": "Moat = Aeroplane brand + 37-country distribution + procurement scale; AI irrelevant.",
        "RevGrowthCeiling": "India basmati exports ~$5-6bn; share gains cap out in mid-single-digit share; FMCG staples extend runway.",
        "GrowthCatalysts": "New export markets; staples cross-sell; basmati price cycles.",
        "StagnationCatalysts": "Paddy cost inflation; export duty/MSP policy; Iran payment disruptions; climate yield risk.",
    },
    "AMIRCHAND": {
        "AI_Moat": "Same as AEROPLANE (duplicate listing): brand + distribution moat, AI irrelevant.",
        "RevGrowthCeiling": "Basmati export share ceiling as AEROPLANE; FMCG staples extend.",
        "GrowthCatalysts": "Export market adds; staples attach; realisation cycles.",
        "StagnationCatalysts": "Paddy cost; trade policy; climate yield.",
    },
    "ALPINETEX": {
        "AI_Moat": "Job-work processor - no moat; AI irrelevant.",
        "RevGrowthCeiling": "Processing-capacity bound; ceiling low.",
        "GrowthCatalysts": "Utilisation; capacity additions.",
        "StagnationCatalysts": "Textile cycle; chemical/power costs; effluent compliance.",
    },
    "AMAGI": {
        "AI_Moat": "AI is the battleground: automated playout/ad-insertion strengthens platform stickiness, but gen-AI content commoditises channels. Moat preserved only via first-mover AI features in broadcast chain.",
        "RevGrowthCeiling": "Global cloud playout/streaming monetisation growing fast; ceiling high.",
        "GrowthCatalysts": "Streaming revenue-share scale; new geographies; ad-tech attach.",
        "StagnationCatalysts": "Linear TV decline outpacing streaming; hyperscaler competition; take-rate pressure.",
    },
    "ARDEE": {
        "AI_Moat": "Moat = recycling permits + scrap collection network; AI neutral. Li-ion transition long-term threat to lead-acid demand.",
        "RevGrowthCeiling": "Lead demand tied to auto replacements/UPS/telecom; ceiling low-moderate.",
        "GrowthCatalysts": "Scrap availability; LME spread; capacity adds.",
        "StagnationCatalysts": "EV transition cutting lead-acid volumes; lead price cycle; environmental compliance costs.",
    },
    "AYE": {
        "AI_Moat": "Moat = branch-based micro-MSME underwriting; fintech AI credit-scoring medium-term threat; own AI models partial defence. Mixed.",
        "RevGrowthCeiling": "Micro-MSME credit gap lakhs of crores; ceiling high.",
        "GrowthCatalysts": "Branch expansion; ticket-size growth; healthy portfolio quality.",
        "StagnationCatalysts": "Unsecured-lending credit cycle; microfinance regulation tightening; yield compression from competition.",
    },

    # ---------------- Batch B ----------------
    "BLUEJET": {
        "AI_Moat": "AI/computer-aided diagnosis increases scan volumes and early detection = structural contrast-media demand tailwind. Moat = iodinated chemistry mastery + decades-long pharma qualifications; durable.",
        "RevGrowthCeiling": "Global contrast media $5-6bn growing mid-to-high single digit; steady compounder ceiling, not exponential.",
        "GrowthCatalysts": "Contrast media volume growth with global imaging; backward integration into iodine derivatives; new molecules/intermediates.",
        "StagnationCatalysts": "Iodine raw-material cost (Chile/Japan oligopoly); generic price erosion; customer concentration.",
    },
    "BLSE": {
        "AI_Moat": "Real long-term threat: self-service digital govt services + UPI erode assisted CSP model. Moat = CSP network + govt/bank contracts; preserved only while rural India needs handholding.",
        "RevGrowthCeiling": "Tied to govt contract flow and rural transaction volumes; ceiling moderate.",
        "GrowthCatalysts": "New state e-governance contracts; BC banking expansion; allied services (insurance, bill pay, travel) attach.",
        "StagnationCatalysts": "Digitisation making CSPs redundant; contract re-tender losses; bank BC fee cuts.",
    },
    "BLUESTONE": {
        "AI_Moat": "AI design/recommendation tools marginal; moat = brand + omnichannel experience. AI neutral; Titan-scale competition is the real battle.",
        "RevGrowthCeiling": "India jewellery ~$85-100bn with organised share still shifting - ceiling high.",
        "GrowthCatalysts": "Store expansion; studded/diamond mix improving margin; online-to-store funnel conversion.",
        "StagnationCatalysts": "Gold price spikes denting volumes; Titan/Senco competition; inventory working-capital drag.",
    },
    "BANSALWIRE": {
        "AI_Moat": "Commodity converter; moat = scale + speciality-wire qualifications. AI irrelevant.",
        "RevGrowthCeiling": "India wire industry Rs 25-30k cr fragmented; single-digit volume growth + mix shift; ceiling moderate.",
        "GrowthCatalysts": "Speciality wire share (auto, fasteners, tools); exports; operating leverage.",
        "StagnationCatalysts": "Steel rod cost swings; auto demand cyclicality; import competition.",
    },
    "BELRISE": {
        "AI_Moat": "Safety-critical supplier qualification moat durable; robotics/AI improves own plants. Real risk = EV simplification cutting sheet-metal/casting content per vehicle, not AI.",
        "RevGrowthCeiling": "Tied to 2W/car production cycles (~single-digit); ceiling low-moderate without diversification.",
        "GrowthCatalysts": "New OEM program wins; exports; interest savings post-IPO (borrowings halved).",
        "StagnationCatalysts": "2W demand stagnation; EV part simplification; steel cost; customer concentration.",
    },
    "BMWVENTLTD": {
        "AI_Moat": "Distribution spread business - no moat; AI irrelevant.",
        "RevGrowthCeiling": "Steel volume x thin spread; 3-4% OPM caps economics; ceiling low.",
        "GrowthCatalysts": "Steel consumption cycle; PEB fabrication demand; PVC pipes volume.",
        "StagnationCatalysts": "Steel price downturns squeezing spread; working-capital bloat; interest cost.",
    },
    "BHARTIHEXA": {
        "AI_Moat": "AI-era data consumption lifts ARPU; telecom = 3-player infrastructure moat, AI a demand tailwind.",
        "RevGrowthCeiling": "Capped at 2 circles (Rajasthan, NE); growth = ARPU + broadband mix, single-digit to low-teens.",
        "GrowthCatalysts": "Tariff hikes; subscriber mix-up to higher ARPU plans; home broadband cross-sell.",
        "StagnationCatalysts": "Jio price aggression; rural income weakness; spectrum/network capex burden.",
    },
    "BAJAJHFL": {
        "AI_Moat": "Moat = Bajaj Finance distribution + lowest-quartile funding cost; AI underwriting is table stakes, neutral.",
        "RevGrowthCeiling": "Housing credit Rs 33-35 lakh cr market; book can compound 20%+ for years - ceiling distant.",
        "GrowthCatalysts": "AUM growth 25-30%; developer finance and LAP segments; cost-of-funds advantage.",
        "StagnationCatalysts": "Property cycle downturn; rising credit costs; bank competition on mortgage pricing.",
    },
    "BLACKBUCK": {
        "AI_Moat": "Network-effect moat (shippers x truckers) moderate; AI load-matching/route optimisation = take-rate advantage to first mover. AI tailwind if deployed ahead of peers.",
        "RevGrowthCeiling": "$150bn+ Indian trucking, digital penetration low - ceiling high.",
        "GrowthCatalysts": "Freight matching volumes; toll/fuel payments attach; fleet telematics subscriptions.",
        "StagnationCatalysts": "Freight-rate downturns; trucker churn to rivals; regulation of payments margin.",
    },
    "BRIGHOTEL": {
        "AI_Moat": "Asset moat (prime South India locations) + Marriott brands - AI-proof; AI travel booking mild channel risk only.",
        "RevGrowthCeiling": "Occupancy x rate cycle bounded; growth = new hotel additions; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; occupancy recovery; new hotel openings.",
        "StagnationCatalysts": "Travel demand shocks; OTA commission creep; renovation capex cycles.",
    },
    "BALAJEE": {
        "AI_Moat": "Commodity industrial packaging - no moat; AI irrelevant.",
        "RevGrowthCeiling": "Export FIBC demand, capacity-bound; ceiling low.",
        "GrowthCatalysts": "Capacity utilisation; export order wins; PP price spread.",
        "StagnationCatalysts": "PP cost; global agro/chemical demand dips; price competition.",
    },
    "BORANA": {
        "AI_Moat": "Commodity grey fabric weaver - no moat; AI irrelevant.",
        "RevGrowthCeiling": "Ceiling = loom capacity; growth capex-driven (46% FY25), textile-cycle bound.",
        "GrowthCatalysts": "Capacity ramp; export demand; polyester yarn-to-fabric spread.",
        "StagnationCatalysts": "Polyester cost; Surat overcapacity; textile demand dips.",
    },
    "BHARATCOAL": {
        "AI_Moat": "Natural-resource moat (Jharia reserves) irreplaceable; AI neutral. Coking coal for steel harder to substitute than thermal; long-term green-steel (H2 DRI) the structural threat.",
        "RevGrowthCeiling": "58.5% domestic coking coal share; import substitution runway (demand 67 to 138 mn MT by FY35) - ceiling moderate-high.",
        "GrowthCatalysts": "Mine reopenings; washed-coal premium; volume growth with steel capex.",
        "StagnationCatalysts": "Notified prices vs PSU wage inflation (H1 FY26 PAT crash); ESG-driven steel decarbonisation; legacy mine fires/subsidence costs.",
    },
    "BLEL": {
        "AI_Moat": "Niche metal rolls (10-11.5% domestic share) with recurring wear-out replacement + qualification lock-in; moat moderate. AI neutral.",
        "RevGrowthCeiling": "Tied to steel-plant production/capex cycles; ceiling low-moderate.",
        "GrowthCatalysts": "Alloy steel bar demand; export share (21 countries); castings for steel/mining/sugar plants.",
        "StagnationCatalysts": "Steel-sector capex pauses; scrap/raw material cost; import competition.",
    },

    # ---------------- Batch C ----------------
    "CPPLUS": {
        "AI_Moat": "AI video analytics shifts value from hardware to software - both opportunity (AI cameras, VMS) and threat (Hikvision/Dahua AI scale). Moat = dealer network + 43% share; preserved only if AI software attach leads.",
        "RevGrowthCeiling": "India surveillance growing with infra/smart cities; ceiling moderate-high while organised share shifts.",
        "GrowthCatalysts": "AI-enabled camera upgrades; enterprise/solutions attach; government safe-city projects.",
        "StagnationCatalysts": "Chinese brand price wars; commoditisation of basic cameras; government tender pauses.",
    },
    "CYIENTDLM": {
        "AI_Moat": "AI/datacom hardware demand lifts EMS; defence electronics qualification lock-in durable. Moat preserved via certifications; AI tailwind.",
        "RevGrowthCeiling": "India defence electronics + med-device EMS growing fast; capacity-bound near term; ceiling high.",
        "GrowthCatalysts": "Defence order ramp; industrial segment surge (+397%); AI-server assembly wins.",
        "StagnationCatalysts": "Component supply chains; customer concentration; margin dilution from mix.",
    },
    "CEIGALL": {
        "AI_Moat": "EPC execution moat (elevated structures specialisation); AI neutral - construction is physical. Moat moderate.",
        "RevGrowthCeiling": "Road EPC order flow tied to govt capex; ceiling moderate; receivables cycle caps growth quality.",
        "GrowthCatalysts": "Elevated-project awards; execution pace; order book pipeline.",
        "StagnationCatalysts": "Govt payment delays (101 debtor days); bitumen/steel costs; aggressive bidding.",
    },
    "CBAZAAR": {
        "AI_Moat": "AI-generated fashion imagery/recommendation helps merchandising; moat thin - niche ethnic e-tail vs Myntra/Nykaa scale. AI weak defender.",
        "RevGrowthCeiling": "NRI ethnic wear niche, small base (Rs 27 cr) - ceiling low unless category expands.",
        "GrowthCatalysts": "US/UK NRI demand recovery; ad-efficiency via AI; product range.",
        "StagnationCatalysts": "Ad cost inflation; returns/logistics cost; fast-fashion competition.",
    },
    "CONCORDBIO": {
        "AI_Moat": "Fermentation-process mastery + global transplant-API leadership = sticky qualification moat; AI neutral-to-positive (biotech process optimisation).",
        "RevGrowthCeiling": "Niche immunosuppressant APIs grow with transplant volumes (single-digit); formulations extend; ceiling moderate.",
        "GrowthCatalysts": "Formulations share; new fermentation molecules; API volume recovery.",
        "StagnationCatalysts": "Price erosion (OPM 42% to 35%); inventory build (485 days); regulatory actions.",
    },
    "CARRARO": {
        "AI_Moat": "Tier-1 driveline qualification + global Carraro R&D moat durable; AI/autonomous farm equipment long-term changes driveline design but Carraro adapts with parent. AI neutral.",
        "RevGrowthCeiling": "Tied to tractor (~9 lakh units/yr) and CE cycles; ceiling low-moderate.",
        "GrowthCatalysts": "Tractor volume cycle; exports via Carraro network; OPM recovery (7% to 9-10%).",
        "StagnationCatalysts": "Monsoon-driven tractor demand; EV farm equipment transition; parent-level strategic shifts.",
    },
    "CAPITALSFB": {
        "AI_Moat": "Moat = low-cost deposit franchise in smaller cities (relationship banking); AI scoring helps asset quality but bigtech/fintech threat medium-term. Mixed.",
        "RevGrowthCeiling": "Branch-led model grows 15-20%; regional Punjab-heavy concentration caps ceiling moderate.",
        "GrowthCatalysts": "Deposit growth (Rs 10,018 cr); agri/MSME loan demand; branch expansion.",
        "StagnationCatalysts": "Agri stress events; deposit rate competition; GNPA creep (2.47%).",
    },
    "CANHLIFE": {
        "AI_Moat": "Bancassurance moat (Canara Bank branch monopoly) durable; AI underwriting/servicing efficiency gain. AI neutral-positive.",
        "RevGrowthCeiling": "Tied to Canara Bank distribution and life-insurance penetration; ceiling moderate-high.",
        "GrowthCatalysts": "Bancassurance premium growth; protection mix shift; ULIP equity-cycle tailwind.",
        "StagnationCatalysts": "Bank partner concentration; equity market downturns hitting ULIP; regulatory commission caps.",
    },
    "CAPINVIT": {
        "AI_Moat": "Annuity infrastructure assets - AI-proof cash flows. Moat = NHAI counterparty + AAA debt access.",
        "RevGrowthCeiling": "Grows only via drop-down acquisitions from sponsor; ceiling = sponsor pipeline and leverage caps.",
        "GrowthCatalysts": "Road asset drop-downs; debt refinancing gains; annuity indexation.",
        "StagnationCatalysts": "Acquisition drought; interest-rate spikes; NHAI payment delays.",
    },
    "CRAMC": {
        "AI_Moat": "Moat = Canara Bank distribution (51%) + 30-yr joint-venture stability; AI robo-advisory a mild long-term threat to active funds. AI neutral near-term.",
        "RevGrowthCeiling": "India MF AUM ~Rs 70 lakh cr compounding; mid-sized AMC can grow mid-teens; ceiling moderate-high.",
        "GrowthCatalysts": "SIP inflows via bank channel; equity market AUM mark-up; active-to-passive mix management.",
        "StagnationCatalysts": "Equity bear markets; passive ETF shift eroding fees; bank-channel overdependence.",
    },
    "CAPILLARY": {
        "AI_Moat": "AI is the product: loyalty analytics increasingly AI-native - incumbency with 415+ brands is data advantage, but AI-native rivals (and hypersaler CX suites) can disintermediate. Moat must be re-earned via AI features.",
        "RevGrowthCeiling": "Global loyalty mgmt $5-10bn double-digit; ceiling high.",
        "GrowthCatalysts": "AI analytics cross-sell into existing brands; multi-year contract renewals; new geos.",
        "StagnationCatalysts": "CRM giants (Salesforce/Adobe) bundling loyalty; churn to point solutions; thin profitability.",
    },
    "CEWATER": {
        "AI_Moat": "Water-treatment process engineering moat moderate (ZLD design know-how); AI process optimisation incremental. AI neutral.",
        "RevGrowthCeiling": "Industrial water/ZLD demand grows with pollution norms; lumpy project order book; ceiling moderate.",
        "GrowthCatalysts": "ZLD mandate expansion; CBG plants; recurring O&M/spares build.",
        "StagnationCatalysts": "Capex deferral by industry; negative O&M (-3.49% margin); competition from Va Tech Wabag.",
    },
    "CELLO": {
        "AI_Moat": "Brand + distribution moat (household name) AI-proof; AI neutral.",
        "RevGrowthCeiling": "Mature categories (pens, houseware) grow with GDP ~8-10%; ceiling moderate.",
        "GrowthCatalysts": "New categories (glassware, appliances); distribution depth; export potential.",
        "StagnationCatalysts": "Polymer cost crushing OPM (10% to 3.2%); cheap unorganised competition; category maturity.",
    },
    "CRIZAC": {
        "AI_Moat": "Agent-network matching moat relationship-based; AI direct-application platforms (universities going direct-to-student) = real disintermediation threat long-term. AI net threat.",
        "RevGrowthCeiling": "~1.3 mn Indian students abroad, commission pool $3-5bn; ceiling moderate.",
        "GrowthCatalysts": "UK placement volumes; Canada/Australia visa recovery; new university partnerships.",
        "StagnationCatalysts": "Visa policy tightening (Canada caps); universities bypassing agents; commission-rate cuts.",
    },
    "CLEANMAX": {
        "AI_Moat": "AI data-centre power demand = structural tailwind for C&I renewables. Moat = land + interconnect + C&I contracts; AI-proof.",
        "RevGrowthCeiling": "India C&I clean-power market early (#1 with just 8% share); ceiling high - GW pipeline.",
        "GrowthCatalysts": "C&I corporate contracting; new state open-access; carbon-credit revenue.",
        "StagnationCatalysts": "Interest burden (Rs 369 cr) on Rs 8,000 cr debt; open-access policy changes; discom pushback.",
    },
    "CMLL": {
        "AI_Moat": "MDO contract-mining relationships with Coal India = moderate moat; AI/autonomous hauling an efficiency tool not threat. AI neutral.",
        "RevGrowthCeiling": "Order book Rs 9,551 cr (~3x revenue) gives visibility; Coal India 1 bn tonne target extends runway; ceiling moderate.",
        "GrowthCatalysts": "New MDO contracts; fleet expansion; rake-logistics share.",
        "StagnationCatalysts": "Diesel cost; D/E 1.63 leverage; Coal India payment delays; coal transition politics.",
    },
    "CMPDI": {
        "AI_Moat": "61% mining-consultancy share + Coal India captive demand = durable; AI geology/mine-planning tools could commoditise studies long-term. AI mild threat, expertise moat holds near-term.",
        "RevGrowthCeiling": "Tied to Coal India capex and national mineral exploration programs; ceiling moderate.",
        "GrowthCatalysts": "Coal expansion consultancy (66% of revenue); mineral exploration missions; ESG/environmental studies.",
        "StagnationCatalysts": "OPM slide (42% to 34%) from wage costs; PSU pricing constraints; private-mining policy shifts.",
    },
    "CMRGREEN": {
        "AI_Moat": "Largest secondary-aluminium capacity (~4x rival) + scrap-collection network = scale moat; AI sorting tech improves yields. AI mild positive.",
        "RevGrowthCeiling": "India recycled aluminium 2.16 mn MT growing with EV/aluminium demand; ceiling high for #1 player.",
        "GrowthCatalysts": "Aluminium demand from EV lightweighting; new rolled/extrusion segments; scrap availability scale.",
        "StagnationCatalysts": "2-4% OPM spread business - LME/scrap spread squeezes; import duty changes on scrap; auto cycle dips.",
    },
    "CORDELIA": {
        "AI_Moat": "Single-ship cruise monopoly in India = niche asset moat; AI irrelevant. Moat = first-mover + port relationships.",
        "RevGrowthCeiling": "Tiny base (549k passengers cumulative); single ship caps revenue until fleet adds; ceiling moderate with ships, low without.",
        "GrowthCatalysts": "Occupancy/yield recovery; second ship; Lakshadweep route popularity.",
        "StagnationCatalysts": "Fuel/port cost inflation (PAT -69%); geopolitical route risks; D/E 1.27 leverage.",
    },
    "CORONA": {
        "AI_Moat": "Branded-prescription moat (doctor relationships, #5 women's health) durable; AI diagnosis tools reinforce specialist prescribing. AI neutral-positive.",
        "RevGrowthCeiling": "IPM grows ~10%; focused-portfolio ceiling moderate.",
        "GrowthCatalysts": "Women's health franchise; new launches; marketing efficiency (OPM 15% to 21%).",
        "StagnationCatalysts": "NLEM price control; patent expiries on acquired brands; marketing-cost inflation.",
    },
    "CSM": {
        "AI_Moat": "GovTech domain moat = long govt relationships + DPI implementation know-how; AI-gov services could streamline but procurement lock-in protects. AI mild tool.",
        "RevGrowthCeiling": "India + Africa govt IT budgets niche; order book Rs 358 cr; ceiling moderate.",
        "GrowthCatalysts": "African DPI expansions; India mining-tech contracts; export consulting.",
        "StagnationCatalysts": "Lumpy deal flow; 154 debtor days; African currency risk; election-cycle pauses.",
    },

    # ---------------- Batch D ----------------
    "DAMCAPITAL": {
        "AI_Moat": "Relationship-trust moat in M&A/ECM advisory - AI deal-screening boosts productivity, cannot replace founder-level deal trust. Moat holds.",
        "RevGrowthCeiling": "Deal-cycle dependent; India ECM fee pool $1bn+ in boom years; ceiling moderate and cyclical.",
        "GrowthCatalysts": "IPO pipeline; M&A wave (consolidation); wealth-management AUM build.",
        "StagnationCatalysts": "Bear-market deal droughts; fee competition from larger banks; key-person exits.",
    },
    "DBEIL": {
        "AI_Moat": "Execution moat on public buildings moderate; AI project-management tools marginal. AI neutral.",
        "RevGrowthCeiling": "Tied to govt construction capex flow; ceiling moderate.",
        "GrowthCatalysts": "Hospital/institutional/stadium awards; execution pace; order-book pipeline.",
        "StagnationCatalysts": "Govt payment delays; aggressive tender bidding; election-year capex pauses.",
    },
    "DEEDEV": {
        "AI_Moat": "Refinery-grade piping fabrication certifications = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Tied to India hydrocarbon/industrial capex cycle; ceiling moderate.",
        "GrowthCatalysts": "Refinery/petrochemical expansion programs; export piping-module orders.",
        "StagnationCatalysts": "Capex deferrals; steel cost; larger fabricator competition.",
    },
    "DENTA": {
        "AI_Moat": "Niche groundwater-recharge know-how, thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "Govt water-budget dependent niche; ceiling low-moderate.",
        "GrowthCatalysts": "Jal Jeevan-type program spend; water-scarcity-driven municipal demand.",
        "StagnationCatalysts": "Tender pauses; monsoon variability shifting priorities; competition.",
    },
    "DEVX": {
        "AI_Moat": "Tier-2 flex-office first-mover + enterprise contracts; AI-era distributed/hybrid work tailwind. Moat moderate.",
        "RevGrowthCeiling": "Tier-2 flex demand shallower than metros; ceiling moderate.",
        "GrowthCatalysts": "Centre additions; enterprise committed seats; fit-out and facility-services revenue.",
        "StagnationCatalysts": "Tier-2 demand depth; Awfis/IndiQube entering tier-2; lease rigidity in downturns.",
    },
    "DIFFNKG": {
        "AI_Moat": "Consumable recurrence (welding wire, wear plates) + fabricator brand = moderate moat; robotic-welding adoption raises content. AI neutral.",
        "RevGrowthCeiling": "Rs 8-10k cr welding industry growing with infra; ceiling moderate.",
        "GrowthCatalysts": "Infra/fabrication activity; cement/mining wear-plate demand; exports.",
        "StagnationCatalysts": "Steel input cost; Chinese wire imports; industrial slowdown.",
    },
    "DIVGIITTS": {
        "AI_Moat": "Only-Indian torque-converter/transfer-case maker + OEM qualification lock-in = durable niche. EV transition cuts ICE converter demand but adds EV-transmission work - must pivot. AI neutral.",
        "RevGrowthCeiling": "Tied to SUV/4WD volumes, niche content; ceiling moderate.",
        "GrowthCatalysts": "SUV 4WD content growth; EV transmission program wins; export tooling.",
        "StagnationCatalysts": "EV shift eroding torque-converter TAM; OEM concentration; program cancellations.",
    },
    "DOMS": {
        "AI_Moat": "School-stationery brand + distribution moat; digitalisation nibbles at handwriting but physical school supplies durable. AI neutral.",
        "RevGrowthCeiling": "India stationery ~10% grower; ceiling moderate.",
        "GrowthCatalysts": "School enrolment; premium art-materials mix; export expansion.",
        "StagnationCatalysts": "EdTech/digital classrooms; polymer/wood cost; Camlin Kokuyo/Navneet competition.",
    },
    "DHOOTTRANS": {
        "AI_Moat": "41% 2W/3W harness share + OEM qualifications = cost+scale moat; EV content shift (battery packs, controllers) both threat and extension. AI neutral.",
        "RevGrowthCeiling": "Tied to 2W/3W volumes (single-digit industry); ceiling low-moderate.",
        "GrowthCatalysts": "2W/3W volume cycle; EV battery-pack/controller content; exports.",
        "StagnationCatalysts": "EV harness simplification; OEM annual price cuts; copper cost.",
    },

    # ---------------- Batch E ----------------
    "EBGNG": {
        "AI_Moat": "Refurb operations + bulk IT-asset sourcing relationships = moderate moat; AI device management marginal. AI neutral.",
        "RevGrowthCeiling": "India refurbished IT growing fast off small base (digital inclusion); ceiling moderate-high.",
        "GrowthCatalysts": "Corporate ITAD contracts; SMB affordable-PC demand; e-waste regulation tailwind.",
        "StagnationCatalysts": "New budget-laptop price collapses squeezing refurb value; used-IT import policy; quality perception.",
    },
    "ECOSMOBLTY": {
        "AI_Moat": "Corporate-account stickiness + fleet operations scale = moderate moat; AI dispatch/routing efficiency gain. AI mild positive.",
        "RevGrowthCeiling": "Corporate ground-transport market large but margin-thin; ceiling moderate.",
        "GrowthCatalysts": "Corporate mobility outsourcing; EV-fleet ESG wins; city/country expansion.",
        "StagnationCatalysts": "Corporate travel cost cuts; ride-hailing competition; fuel/driver cost inflation.",
    },
    "ELLEN": {
        "AI_Moat": "Local gas production + tanker/cylinder logistics economics (haulage radius) = moderate-durable moat. AI neutral.",
        "RevGrowthCeiling": "Regional industrial-gas demand; ceiling moderate.",
        "GrowthCatalysts": "Steel/hospital oxygen demand; onsite plant contracts; speciality gases mix.",
        "StagnationCatalysts": "Industrial slowdown; power cost; Linde/Air Liquide scale competition.",
    },
    "EMCURE": {
        "AI_Moat": "India brand moat (women's health, cardiology) + US generics pipeline; AI drug-development speeds pipeline. AI neutral-positive.",
        "RevGrowthCeiling": "India $50bn+ pharma plus global generics; ceiling high.",
        "GrowthCatalysts": "India branded ~10% growth; US launches pipeline; gynaec/cardiology franchise share.",
        "StagnationCatalysts": "US generic price erosion; FDA compliance actions; input-cost spikes.",
    },
    "EMSLIMITED": {
        "AI_Moat": "Water EPC + recurring O&M annuity mix = moderate moat; AI neutral.",
        "RevGrowthCeiling": "AMRUT/JJM water-capex cycle; ceiling moderate.",
        "GrowthCatalysts": "STP/WTP order wins; O&M annuity book build; sewage-network programs.",
        "StagnationCatalysts": "Govt tender delays; receivable cycles; Wabag/peer competition.",
    },
    "ENTERO": {
        "AI_Moat": "Pharmacy-reach distribution network = moderate moat; B2B e-pharma platforms (AI-led) a real disintermediation threat over time.",
        "RevGrowthCeiling": "Thin-spread distribution economics; ceiling moderate.",
        "GrowthCatalysts": "Portfolio breadth (more manufacturers); geographic reach; automation efficiency.",
        "StagnationCatalysts": "Manufacturers going direct; B2B e-pharma platform competition; credit losses on retailers.",
    },
    "EPACK": {
        "AI_Moat": "ODM design+cost+speed moat thin-moderate - brands own the demand; switching possible but re-qualification costly. AI neutral.",
        "RevGrowthCeiling": "India room-AC market 11-12 mn units with low penetration - ceiling high with capacity adds.",
        "GrowthCatalysts": "AC demand (income growth, summers); new brand customers; component backward integration.",
        "StagnationCatalysts": "Customer concentration; copper/aluminium cost; weak-summer season failure.",
    },
    "EPACKPEB": {
        "AI_Moat": "PEB design-engineering + project delivery moderate moat; AI design tools incremental. AI neutral.",
        "RevGrowthCeiling": "India PEB Rs 15-20k cr growing double-digit (warehouses, factories); ceiling moderate-high.",
        "GrowthCatalysts": "Logistics/warehouse build-out; PLI factory construction; export PEB orders.",
        "StagnationCatalysts": "Industrial capex pauses; steel cost; Kirby/Zamil competition.",
    },
    "ESAFSFB": {
        "AI_Moat": "JLG microfinance model + gold-loan pivot = moderate moat; AI credit-scoring a tool, fintech threat mild. Mixed.",
        "RevGrowthCeiling": "MFI Rs 4-5 lakh cr + gold Rs 4-6 lakh cr pools; ceiling high once book health restored.",
        "GrowthCatalysts": "Gold-loan ramp; MFI book recovery; deposit franchise rebuild.",
        "StagnationCatalysts": "MFI credit-cycle stress (elevated GNPA); regulatory microfinance tightening; funding cost.",
    },
    "EIEL": {
        "AI_Moat": "Water EPC + O&M moat moderate; AI neutral.",
        "RevGrowthCeiling": "JJM/AMRUT capex cycle bound; ceiling moderate.",
        "GrowthCatalysts": "Sewage/water O&M annuities; solar/BESS project attach; hybrid annuity model (HAM) wins.",
        "StagnationCatalysts": "Govt receivables; tender aggression; execution cost overruns.",
    },
    "EUROPRATIK": {
        "AI_Moat": "Brand + distribution moat thin (outsourced manufacturing); AI design tools commoditise aesthetics - mild threat. Distribution is the real asset.",
        "RevGrowthCeiling": "Home-interior demand cycle; ceiling moderate.",
        "GrowthCatalysts": "Housing-completion interior boom; retail distribution depth; new decor categories.",
        "StagnationCatalysts": "Housing slowdown; outsourced-manufacturing supply risk; fashion/taste shifts.",
    },
    "EXCELSOFT": {
        "AI_Moat": "AI is existential battleground: AI-native assessment rivals and AI-assisted cheating undermine legacy LMS/exam platforms; moat must pivot to AI-proctoring and AI-first learning fast.",
        "RevGrowthCeiling": "Global digital assessment tens of billions; ceiling moderate-high only with AI pivot.",
        "GrowthCatalysts": "Online exam volumes (govt recruitment); university digitisation; AI-proctoring demand surge.",
        "StagnationCatalysts": "AI cheating arms race; education-budget cycles; edtech client financial stress.",
    },
    "EXICOM": {
        "AI_Moat": "Telecom DC-power installed base sticky; EV-charger brand + CPO/utility relationships; AI/datacentre power demand spillover positive. Moat moderate.",
        "RevGrowthCeiling": "India EV-charging market multiplying with EV adoption; ceiling high.",
        "GrowthCatalysts": "Public DC fast-charging buildout; home-charger OEM tie-ups; 5G telecom power upgrades.",
        "StagnationCatalysts": "EV adoption pace; Chinese charger import price wars; CPO economics stress.",
    },
    "EMMVEE": {
        "AI_Moat": "Integrated cell+module scale moat moderate; AI datacentre energy demand tailwind; commodity pricing cyclical. AI net positive on demand.",
        "RevGrowthCeiling": "India 500 GW target gives demand runway; ceiling high but margin-cyclical.",
        "GrowthCatalysts": "ALMM-protected domestic demand; cell integration margin; Europe/US exports.",
        "StagnationCatalysts": "Chinese overcapacity price crashes; ALMM/duty policy shifts; polysilicon cost.",
    },

    # ---------------- Batch F ----------------
    "FABTECH": {
        "AI_Moat": "Pharma-capex engineering + cleanroom validation know-how = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India pharma capex cycle structural (bio-CDMO boom); ceiling moderate-high.",
        "GrowthCatalysts": "Pharma capacity expansions; cleanroom standard upgrades; regulated-market project wins.",
        "StagnationCatalysts": "Pharma capex pauses; peer competition; project execution risk.",
    },
    "FEDFINA": {
        "AI_Moat": "Federal Bank parent funding + trust moat; gold-loan underwriting simple. AI neutral. Moat moderate.",
        "RevGrowthCeiling": "Gold + mortgage markets large; ceiling high.",
        "GrowthCatalysts": "Gold-loan shift from unorganised; home loans via Federal network; LAP growth.",
        "StagnationCatalysts": "Gold price volatility (LTV management); banks entering gold loans; credit costs.",
    },
    "FIRSTCRY": {
        "AI_Moat": "Category leadership + private brands + loyalty; AI personalisation marginal edge; the sharper threat is quick-commerce entering babycare. AI neutral.",
        "RevGrowthCeiling": "India babycare $10bn+ growing 10-15%; ceiling high.",
        "GrowthCatalysts": "Online penetration; private-label mix; omnichannel store adds.",
        "StagnationCatalysts": "Quick-commerce (Blinkit/Zepto) competition; discount burn; falling fertility demographics.",
    },
    "FLAIR": {
        "AI_Moat": "Brand + 115-country distribution moderate moat; digital note-taking erodes category slowly. AI mild negative on demand.",
        "RevGrowthCeiling": "Writing instruments mature category; ceiling low.",
        "GrowthCatalysts": "Export markets; premium pens; stationery diversification.",
        "StagnationCatalysts": "Digitalisation; plastic cost; Chinese volume competition.",
    },
    "FRACTAL": {
        "AI_Moat": "AI is the product: Fortune-500 entrenchment + GenAI products (Vaidya, Eugene) + talent moat - but AI services competition exploding (hyperscalers, Big 4, AI-native boutiques); moat re-earned constantly.",
        "RevGrowthCeiling": "Global AI services TAM huge; ceiling high.",
        "GrowthCatalysts": "Enterprise GenAI adoption wave; product revenue scaling; healthcare/CPG vertical depth.",
        "StagnationCatalysts": "AI implementation commoditisation; talent cost wars; billing-rate pressure.",
    },

    # ---------------- Batch G ----------------
    "GALAPREC": {
        "AI_Moat": "Precision spring engineering + 750-SKU qualification base = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Tied to auto/EV/rail component content; niche; ceiling moderate.",
        "GrowthCatalysts": "EV content per vehicle; railway orders; export SKU additions.",
        "StagnationCatalysts": "Auto cycle downturns; steel wire cost; OEM price cuts.",
    },
    "GANDHAR": {
        "AI_Moat": "Speciality white-oil refining + pharma/cosmetic certifications = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Niche ultra-pure oil demand, capacity-bound; ceiling moderate.",
        "GrowthCatalysts": "Pharma/cosmetic-grade demand; capacity expansion; export grades.",
        "StagnationCatalysts": "Base oil cost; cosmetic regulatory shifts; refiner competition.",
    },
    "GANESHCP": {
        "AI_Moat": "Branded staple (Ganesh Atta) + grocery distribution = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Branded-flour shift from loose atta; ceiling moderate.",
        "GrowthCatalysts": "North-India brand penetration; product extensions (besan, sattu); distribution depth.",
        "StagnationCatalysts": "Wheat cost; unorganised competition; thin staple margins.",
    },
    "GAJA": {
        "AI_Moat": "AIF moat = investment track record + LP relationships; AI screening marginal. Moat is performance, not tech.",
        "RevGrowthCeiling": "India AIF fee pool growing but niche; ceiling moderate.",
        "GrowthCatalysts": "New fund raises; real-estate credit deal flow; performance fees on exits.",
        "StagnationCatalysts": "Real estate valuation downturns; LP redemptions; SEBI AIF rule changes.",
    },
    "GARUDA": {
        "AI_Moat": "EPC execution + O&M/MEP services mix = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Construction order flow bound; ceiling moderate.",
        "GrowthCatalysts": "Infra awards; recurring O&M book; MEP services share.",
        "StagnationCatalysts": "Receivables; tender margin aggression; govt capex cycles.",
    },
    "GEMAROMA": {
        "AI_Moat": "Specialty aroma chemistry + customer qualification (70 products) = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Global F&F ingredients niche growing with personal care; ceiling moderate.",
        "GrowthCatalysts": "Fragrance/personal-care demand; new molecules; export share.",
        "StagnationCatalysts": "Raw-material volatility; Chinese competition; FMCG demand dips.",
    },
    "GKENERGY": {
        "AI_Moat": "PM-KUSUM installer moat thin, policy-dependent; AI neutral.",
        "RevGrowthCeiling": "Tied to govt subsidy budget allocations; lumpy; ceiling moderate.",
        "GrowthCatalysts": "PM-KUSUM fund flow; off-grid solar pump demand; O&M attach.",
        "StagnationCatalysts": "Subsidy cuts/budget delays; bidding price wars; good monsoons cutting pump urgency.",
    },
    "GLOTTIS": {
        "AI_Moat": "Customs relationships + EXIM logistics network = moderate moat; AI freight-matching platforms compress brokerage margins - mild threat, own digitalisation offsets.",
        "RevGrowthCeiling": "India logistics double-digit growth; asset-light margins thin; ceiling moderate-high.",
        "GrowthCatalysts": "EXIM trade volumes; 3PL contract wins; warehousing capacity adds.",
        "StagnationCatalysts": "Global trade slowdowns; freight-rate crashes; margin thinness.",
    },
    "GLOBECIVIL": {
        "AI_Moat": "Road EPC execution moat moderate; AI neutral.",
        "RevGrowthCeiling": "NHAI award flow bound; ceiling moderate.",
        "GrowthCatalysts": "Order wins; execution pace; road-asset monetisation cycle.",
        "StagnationCatalysts": "Receivables; bitumen cost; tender aggression.",
    },
    "GODAVARIB": {
        "AI_Moat": "Integrated sugar-ethanol biorefinery moat moderate; AI neutral.",
        "RevGrowthCeiling": "Sugar cyclical; E20 ethanol mandate extends runway; ceiling moderate.",
        "GrowthCatalysts": "Ethanol offtake (E20); bio-based chemicals; sugar price upcycles.",
        "StagnationCatalysts": "Sugar price crashes; cane arrears; ethanol pricing disputes.",
    },
    "GODIGIT": {
        "AI_Moat": "Digital-first underwriting + partnership distribution; AI claims automation is a genuine cost edge - tailwind if scaled ahead of incumbents. Moat moderate, building.",
        "RevGrowthCeiling": "Underpenetrated India general insurance; ceiling high.",
        "GrowthCatalysts": "Motor/health attach; partnership distribution; product innovation (sachet covers).",
        "StagnationCatalysts": "Loss-ratio spikes (weather/events); digital acquisition cost; incumbent price response.",
    },
    "GOPAL": {
        "AI_Moat": "Ethnic-snack brand + Gujarat-strong distribution = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India savoury snacks Rs 40-60k cr; ceiling moderate.",
        "GrowthCatalysts": "Expansion beyond Gujarat; modern trade/quick-commerce; new snack categories.",
        "StagnationCatalysts": "Regional taste shifts; palm oil cost; Haldiram/Bikaji scale competition.",
    },
    "GSLSU": {
        "AI_Moat": "Quarry reserves + stone processing = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Global stone/quartz demand, export-cycle bound; ceiling moderate.",
        "GrowthCatalysts": "Engineered quartz countertop demand; export markets; processing capacity.",
        "StagnationCatalysts": "Construction cycles; freight cost; Chinese quartz dumping.",
    },
    "GROWW": {
        "AI_Moat": "DIY-investor app UX + brand moat moderate; AI advisory commoditises execution further - threat and tool; AI-first features defend engagement.",
        "RevGrowthCeiling": "Retail participation rising (19 cr demat); ceiling high but regulatory risk on F&O.",
        "GrowthCatalysts": "User monetisation; MF/ETF AUM build; new product attach (gold, bonds).",
        "StagnationCatalysts": "F&O regulatory crackdowns; bear-market activity drop; fee compression.",
    },
    "GPTHEALTH": {
        "AI_Moat": "Eastern-India hospital brand + doctor base = moderate moat; AI diagnostics an assist. AI neutral-positive.",
        "RevGrowthCeiling": "Regional healthcare demand, bed-capacity bound; ceiling moderate.",
        "GrowthCatalysts": "Occupancy/ARPOB growth; speciality additions; bed expansions.",
        "StagnationCatalysts": "Doctor dependence; capex drag; pricing regulation.",
    },
    "GKSL": {
        "AI_Moat": "Central-Gujarat nephrology-focused hospital brand = moderate local moat; AI neutral.",
        "RevGrowthCeiling": "Regional kidney-care demand; capacity bound; ceiling moderate.",
        "GrowthCatalysts": "Dialysis/transplant volumes; speciality mix; capacity adds.",
        "StagnationCatalysts": "Doctor attrition; capex funding; regional chain competition.",
    },
    "GSPCROP": {
        "AI_Moat": "Agrochem formulations + registrations + distributor network = moderate moat; precision agriculture reducing pesticide volumes is the long-term threat.",
        "RevGrowthCeiling": "India agrochem mid-single-digit grower; ceiling moderate.",
        "GrowthCatalysts": "New molecule registrations; export registrations; brand portfolio.",
        "StagnationCatalysts": "Monsoon failure; Chinese technicals price swings; biopesticide substitution.",
    },
    "INTERARCH": {
        "AI_Moat": "PEB design (TRAC/TRACDEK) + execution track = moderate moat; AI design tools incremental. AI neutral.",
        "RevGrowthCeiling": "India PEB Rs 15-20k cr double-digit growth; ceiling moderate-high.",
        "GrowthCatalysts": "Warehouse/factory build-out; complex-structure premium; exports.",
        "StagnationCatalysts": "Industrial capex pauses; steel cost; PEB competition.",
    },

    # ---------------- Batch H ----------------
    "HAPPYFORGE": {
        "AI_Moat": "Forging+machining scale with CV/tractor OEM qualification = moderate-durable moat; AI neutral. EV transition erodes crankshaft content, axle/industrial forgings remain.",
        "RevGrowthCeiling": "Tied to CV/tractor/industrial demand cycles; ceiling moderate.",
        "GrowthCatalysts": "CV cycle recovery; industrial forging diversification; export machining.",
        "StagnationCatalysts": "CV demand stagnation; EV engine-part erosion; steel cost.",
    },
    "HONASA": {
        "AI_Moat": "D2C brand-building moat thin - AI content generation lowers entry barriers for rival brands; existing moat = Mamaearth brand equity + omnichannel distribution. AI mild threat, also own tool.",
        "RevGrowthCeiling": "India beauty/personal-care $30bn growing ~10%; ceiling high.",
        "GrowthCatalysts": "Brand portfolio scaling (Derma Co, Aqualogica); quick-commerce distribution; offline expansion.",
        "StagnationCatalysts": "Quick-commerce margin squeeze; D2C brand churn; celebrity-brand competition; marketing inflation.",
    },
    "HEXT": {
        "AI_Moat": "AI tech services = product moat only as strong as platform IP; competition intense (global AI boutiques); cost-arbitrage delivery helps. Fragile, re-earned.",
        "RevGrowthCeiling": "Global AI services demand huge; ceiling high.",
        "GrowthCatalysts": "GenAI platform adoption; vertical solutions; client wallet expansion.",
        "StagnationCatalysts": "AI services commoditisation; hyperscaler competition; pricing pressure.",
    },
    "HDBFS": {
        "AI_Moat": "HDFC Bank parentage - brand, funding cost, distribution = strong moat; AI underwriting table stakes. AI neutral.",
        "RevGrowthCeiling": "Retail credit market huge; ceiling high.",
        "GrowthCatalysts": "AUM growth 20%+; branch expansion; product cross-sell.",
        "StagnationCatalysts": "Credit cycle downturns; RBI risk-weight changes; bank competition.",
    },
    "HMAAGRO": {
        "AI_Moat": "Buffalo procurement scale + 100% EOU export licences = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India buffalo-meat exports ~$3-4bn; ceiling moderate.",
        "GrowthCatalysts": "SEA/Middle-East demand; capacity expansion; by-product value.",
        "StagnationCatalysts": "Slaughter policy risk; buffalo cost; export restrictions; socio-political risk.",
    },
    "HILINFRA": {
        "AI_Moat": "Toll concessions + road EPC = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Toll revenue traffic-bound; ceiling moderate.",
        "GrowthCatalysts": "Traffic growth; new concessions; EPC order flow.",
        "StagnationCatalysts": "Traffic underperformance; toll-rate caps; leverage.",
    },
    "HEXAGON": {
        "AI_Moat": "Micronutrient premix formulation + pharma-grade certification = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Fortification/nutrition demand growing; ceiling moderate.",
        "GrowthCatalysts": "Food-fortification mandates; global premix contracts; clinical nutrition.",
        "StagnationCatalysts": "Vitamin raw-material volatility; tender-based pricing; client concentration.",
    },
    "HORIZONIND": {
        "AI_Moat": "Grade-A warehouse portfolio with ecom/3PL tenants = asset moat; AI-era logistics (quick-commerce dark stores, DC automation) demand tailwind. AI positive.",
        "RevGrowthCeiling": "India warehousing demand strong; ceiling high.",
        "GrowthCatalysts": "Portfolio GLA expansion; rent escalations; occupancy strength.",
        "StagnationCatalysts": "E-commerce slowdown; micro-market oversupply; leverage cost.",
    },
    "HYUNDAI": {
        "AI_Moat": "Global platform + brand + India manufacturing scale = strong moat; SDV/AI transition an R&D arms race where parent scale defends. AI neutral to moat, real transition cost.",
        "RevGrowthCeiling": "India PV market ~4-4.5 mn units growing 5-7%; #2 player ceiling moderate-high.",
        "GrowthCatalysts": "SUV mix; new model cycle; India export hub; EV portfolio ramp.",
        "StagnationCatalysts": "Maruti/Tata/Mahindra competition; EV transition costs; cyclical demand.",
    },

    # ---------------- Batch I ----------------
    "ICICIAMC": {
        "AI_Moat": "Brand + distribution + scale = strong moat; AI robo-advice mild long-term threat to active fees. AI neutral near-term.",
        "RevGrowthCeiling": "India MF AUM compounding mid-teens; #1 rides market growth; ceiling high.",
        "GrowthCatalysts": "SIP inflows; equity AUM mark-ups; active+passive breadth.",
        "StagnationCatalysts": "Bear markets; TER regulation/ETF shift; distributor channel conflicts.",
    },
    "IDEAFORGE": {
        "AI_Moat": "India drone pioneer protected by procurement policy (import bans) = policy moat; AI autonomy is the product race vs DJI-scale rivals. Moat moderate, policy-shielded.",
        "RevGrowthCeiling": "India drone market expanding fast (survey, defence, agriculture); ceiling high but competitive.",
        "GrowthCatalysts": "Government survey/mapping programs; defence orders; drone-services models.",
        "StagnationCatalysts": "Chinese import liberalisation; tender price wars; execution/working-capital stress.",
    },
    "IGCL": {
        "AI_Moat": "Agrochem technicals+formulations with brand (Insecticides-type) = moderate moat; precision-ag long-term volume threat.",
        "RevGrowthCeiling": "India agrochem mid-single-digit; ceiling moderate.",
        "GrowthCatalysts": "New technicals capacity; brand share; exports.",
        "StagnationCatalysts": "Monsoon failure; Chinese price swings; biopesticide substitution.",
    },
    "IGIL": {
        "AI_Moat": "World's largest independent diamond certifier - trust moat (stones need certification); AI lab-grown detection a core capability arms race. Moat strong; AI both tool and threat.",
        "RevGrowthCeiling": "Tied to global diamond trade volumes; natural-diamond decline a ceiling press; lab-grown adds volume; ceiling moderate.",
        "GrowthCatalysts": "Lab-grown certification demand; India/China lab network; new categories (colored stones).",
        "StagnationCatalysts": "Natural-diamond demand erosion; lab-grown price collapse cutting cert fees; GIA competition.",
    },
    "IKIO": {
        "AI_Moat": "ODM design-to-cost + manufacturing moat thin-moderate; switching costly but possible. AI neutral.",
        "RevGrowthCeiling": "LED market mature; EMS diversification extends runway; ceiling moderate.",
        "GrowthCatalysts": "US retail client wins; EMS assembly mix; new product categories.",
        "StagnationCatalysts": "Client concentration; LED price deflation; US tariff risk.",
    },
    "IKS": {
        "AI_Moat": "Highest AI-disruption exposure: GenAI automates medical coding/billing/RCM - the core service. Moat = clinical-domain trust + physician-lane expertise; must pivot to AI-augmented platform or margins compress. AI threat + opportunity.",
        "RevGrowthCeiling": "US healthcare admin outsourcing TAM huge; ceiling high if AI pivot lands.",
        "GrowthCatalysts": "Client wallet-share expansion; AI-embedded margin gains; US provider outsourcing wave.",
        "StagnationCatalysts": "AI automation compressing RCM pricing; client in-housing AI; US healthcare policy shifts.",
    },
    "INDGN": {
        "AI_Moat": "AI already core to offering (medical content, omnichannel) with top-20 biopharma trust; but GenAI commoditises content services - moat = regulated-industry relationships + data, re-earned via AI products. Battleground.",
        "RevGrowthCeiling": "Biopharma commercialisation spend large; ceiling high.",
        "GrowthCatalysts": "Biopharma wallet share; AI product attach; new-drug-launch services.",
        "StagnationCatalysts": "GenAI fee compression; pharma marketing budget cuts; client in-housing.",
    },
    "INDIASHLTR": {
        "AI_Moat": "Self-employed tier-2/3 underwriting skill + branch moat moderate; AI credit-scoring a tool, fintech threat mild.",
        "RevGrowthCeiling": "Affordable housing finance gap large; ceiling high.",
        "GrowthCatalysts": "Branch expansion; 25%+ AUM compounding; tested credit model.",
        "StagnationCatalysts": "Informal-segment credit events; funding cost; Aavas/Aptus competition.",
    },
    "INDIQUBE": {
        "AI_Moat": "Enterprise flex relationships + building economics = moderate moat; hybrid-work era demand tailwind. AI positive for flex demand.",
        "RevGrowthCeiling": "India flex workspace growing; ceiling moderate-high.",
        "GrowthCatalysts": "Seat additions; enterprise pre-commits; managed-aggregation (asset-light) mix.",
        "StagnationCatalysts": "IT-sector hiring freezes; lease rigidity in downturns; Awfis price competition.",
    },
    "INOXINDIA": {
        "AI_Moat": "Cryogenic engineering IP (LNG, hydrogen, space) = strong niche moat; AI neutral.",
        "RevGrowthCeiling": "Global cryo equipment niche; LNG + green hydrogen extends; ceiling moderate-high.",
        "GrowthCatalysts": "LNG infrastructure buildout; hydrogen/space programs; export share.",
        "StagnationCatalysts": "LNG capex cycles; scale-up execution; Chart Industries global competition.",
    },
    "INNOVACAP": {
        "AI_Moat": "CDMO capacity + regulatory approvals + domestic brands = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India pharma market growth; ceiling moderate-high.",
        "GrowthCatalysts": "CDMO utilisation; branded portfolio expansion; export registrations.",
        "StagnationCatalysts": "Generic price erosion; working-capital bloat; regulatory actions.",
    },
    "INDOFARM": {
        "AI_Moat": "Tractor + pick-and-carry crane manufacturing with dealer network = moderate moat; AI/autonomous farm equipment distant threat. AI neutral.",
        "RevGrowthCeiling": "India tractor industry ~9 lakh units cyclical; niche crane segment; ceiling moderate.",
        "GrowthCatalysts": "Tractor demand cycle; crane fleet replacement; exports.",
        "StagnationCatalysts": "Monsoon-driven demand swings; intense OEM competition (M&M, TAFE, Escorts); commodity cost.",
    },
    "IVALUE": {
        "AI_Moat": "IT distributor-integrator moat thin; AI shifts value to services, hardware margins compress - must build service depth. AI mild threat.",
        "RevGrowthCeiling": "India enterprise IT spend growing; ceiling moderate.",
        "GrowthCatalysts": "Cybersecurity/datacentre demand; services mix shift; vendor partnerships.",
        "StagnationCatalysts": "Hardware margin compression; hyperscaler direct sales; working-capital load.",
    },
    "IXIGO": {
        "AI_Moat": "AI trip-planning both threat (Google/MakeMyTrip AI) and tool (TARA assistant); moat = train-booking niche (ConfirmTatkal) + brand. Thin-moderate, AI battleground.",
        "RevGrowthCeiling": "India OTA market growing; train-first niche; ceiling moderate.",
        "GrowthCatalysts": "Train/air ticket attach; AI-assistant engagement; hotel cross-sell.",
        "StagnationCatalysts": "IRCTC channel risk; Google AI travel planning; discount burn.",
    },
    "IREDA": {
        "AI_Moat": "Sovereign-backed policy mandate within renewables lending = quasi moat; AI neutral.",
        "RevGrowthCeiling": "India energy-transition financing need Rs 30+ lakh cr; ceiling high.",
        "GrowthCatalysts": "Renewable loan book 20%+; new segments (green hydrogen, storage); PSU funding cost edge.",
        "StagnationCatalysts": "Developer stress; interest-rate cycles; discom counterparty quality.",
    },
    "INDOMIM": {
        "AI_Moat": "Metal-injection-moulding process mastery + complex-part qualification = strong niche moat; AI neutral.",
        "RevGrowthCeiling": "Global MIM $4-5bn growing double-digit; ceiling moderate-high for niche leader.",
        "GrowthCatalysts": "EV/medical/consumer-electronics MIM parts; capacity adds; export share.",
        "StagnationCatalysts": "Customer concentration; metal powder cost; machining/casting alternatives.",
    },
    "INNOVISION": {
        "AI_Moat": "Labour staffing moat thin; FASTag/automated tolling erodes toll-plaza manpower line - AI/automation a direct negative.",
        "RevGrowthCeiling": "Staffing demand tied to infra/industry cycles; ceiling low-moderate.",
        "GrowthCatalysts": "Contract staffing demand; govt skill-development programs.",
        "StagnationCatalysts": "Automation of routine roles; thin margins; compliance cost escalation.",
    },

    # ---------------- Batch J ----------------
    "JAINREC": {
        "AI_Moat": "Recycling permits + LME-registered lead brand = moderate moat; AI neutral. Li-ion transition a long-term lead-demand threat.",
        "RevGrowthCeiling": "Scrap availability + metal demand bound; ceiling moderate.",
        "GrowthCatalysts": "Scrap collection scale; LME brand premium; copper/aluminium mix.",
        "StagnationCatalysts": "Metal price crashes; EV lead-acid erosion; environmental compliance cost.",
    },
    "JARO": {
        "AI_Moat": "AI tutoring/credentialing threatens degree-resale model as universities go direct-online; moat = 36 university partnerships. AI real threat.",
        "RevGrowthCeiling": "Online higher-ed enrolment demand; ceiling moderate.",
        "GrowthCatalysts": "New university partnerships; upskilling programs; international degrees.",
        "StagnationCatalysts": "UGC online-degree regulation; AI learning alternatives; enrolment fatigue.",
    },
    "JGCHEM": {
        "AI_Moat": "Zinc-oxide process chemistry + #1 India scale = moderate moat; AI neutral.",
        "RevGrowthCeiling": "ZnO demand tied to tyre/ceramics growth; ceiling moderate.",
        "GrowthCatalysts": "Tyre industry demand; specialty grades (pharma/cosmetic); exports.",
        "StagnationCatalysts": "Zinc cost; import competition; ceramic demand dips.",
    },
    "JIOFIN": {
        "AI_Moat": "Reliance ecosystem distribution + digital-first cost base = strong moat; AI credit underwriting at scale is a genuine edge. AI tailwind.",
        "RevGrowthCeiling": "Multi-segment retail finance TAM huge; ceiling high.",
        "GrowthCatalysts": "Consumer/supplier lending on Reliance network; payments; insurance distribution; AMC build-out.",
        "StagnationCatalysts": "Credit-cycle losses; RBI digital-lending rules; incumbent price responses.",
    },
    "JLHL": {
        "AI_Moat": "Mumbai/West-India hospital brand + doctor base = moderate moat; AI diagnostics an assist. AI neutral-positive.",
        "RevGrowthCeiling": "Regional bed capacity bound; ceiling moderate.",
        "GrowthCatalysts": "Occupancy/ARPOB growth; bed additions; new hospital ramp.",
        "StagnationCatalysts": "Doctor cost inflation; capex drag; Hinduja/Fortis competition.",
    },
    "JNKINDIA": {
        "AI_Moat": "Specialised fired-heater/furnace engineering track record = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Refinery/petrochemical capex cycle bound; ceiling moderate.",
        "GrowthCatalysts": "Indian refinery expansions; export orders; hydrogen-ready furnace work.",
        "StagnationCatalysts": "Capex deferrals; large-EPC bundling; execution slippage.",
    },
    "JNPR": {
        "AI_Moat": "PPA portfolio + land = AI-proof asset moat; AI data-centre power demand a structural tailwind.",
        "RevGrowthCeiling": "Bounded by auction wins and debt capacity; renewable additions pipeline large; ceiling moderate-high.",
        "GrowthCatalysts": "Capacity commissioning; hybrid/peaker plant wins; C&I contracts.",
        "StagnationCatalysts": "Reverse-auction tariff competition; curtailment; interest cost.",
    },
    "JSWCEMENT": {
        "AI_Moat": "Captive group slag (waste-stream feedstock) gives unique GGBS cost moat + green-cement positioning; AI neutral.",
        "RevGrowthCeiling": "India cement demand 5-7% growth + share gains from blended mix; ceiling moderate-high.",
        "GrowthCatalysts": "Capacity expansion; GGBS blending mix; infrastructure demand cycle.",
        "StagnationCatalysts": "Cement cyclicality; slag availability cap; freight/gypsum cost; Adani/Aditya Birla competition.",
    },
    "JSFB": {
        "AI_Moat": "JLG micro + small-business lending with deposit base = moderate moat; AI credit-scoring a tool, not differentiator.",
        "RevGrowthCeiling": "Micro/small-biz credit pools large; ceiling high-ish post-asset-quality repair.",
        "GrowthCatalysts": "Branch expansion; deposit franchise build; book recovery.",
        "StagnationCatalysts": "MFI credit-cycle stress; competition; funding cost.",
    },
    "JSWINFRA": {
        "AI_Moat": "Port assets + hinterland licences = irreplaceable infrastructure moat; AI port-automation an efficiency gain. AI neutral-positive.",
        "RevGrowthCeiling": "India cargo volumes grow with GDP; capacity-expansion bound; ceiling moderate-high.",
        "GrowthCatalysts": "New berth capacity; cargo volume growth; new port concessions; mechanisation margin.",
        "StagnationCatalysts": "Trade cycles; capex execution; Adani port competition.",
    },
    "JUNIPER": {
        "AI_Moat": "Luxury hotel assets + brand positioning = asset moat; AI neutral.",
        "RevGrowthCeiling": "Occupancy x rate cycle; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; new properties; F&B/MICE revenue.",
        "StagnationCatalysts": "Travel demand shocks; rate cyclicality; leverage.",
    },
    "JYOTICNC": {
        "AI_Moat": "CNC/5-axis machine-tool engineering = import-substitution niche moat; smart/AI-embedded manufacturing an opportunity. Moat moderate.",
        "RevGrowthCeiling": "India machine-tool demand growing with Make-in-India; ceiling moderate.",
        "GrowthCatalysts": "Aerospace/auto 5-axis demand; exports; spares/services attach.",
        "StagnationCatalysts": "Capex cycles; DMG/Haas import competition; execution scale-up.",
    },
    "JKIPL": {
        "AI_Moat": "Metro/roads/water EPC execution moat moderate; AI neutral.",
        "RevGrowthCeiling": "Urban-infra (metro) pipeline bound; ceiling moderate.",
        "GrowthCatalysts": "Metro line awards; water projects; execution pace.",
        "StagnationCatalysts": "Govt receivables; tender aggression; execution slippage.",
    },

    # ---------------- Batch K ----------------
    "KALAMANDIR": {
        "AI_Moat": "Saree retail brand + 86-store network = thin-moderate moat; AI neutral (Gen-AI fashion imagery marginal).",
        "RevGrowthCeiling": "Saree demand mature, slowly eroding to western wear; ceiling low.",
        "GrowthCatalysts": "Store additions; online ethnic sales; value-format expansion.",
        "StagnationCatalysts": "Western-wear shift; e-commerce ethnic competition; regional rivals.",
    },
    "KALPATARU": {
        "AI_Moat": "Mumbai land bank + brand + approvals track = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Launch-pipeline bound; ceiling moderate.",
        "GrowthCatalysts": "Mumbai luxury cycle; redevelopment deals; brand launch velocity.",
        "StagnationCatalysts": "Approval delays; Mumbai property downturn; leverage.",
    },
    "KISSHT": {
        "AI_Moat": "AI underwriting IS the model (proprietary default models + app distribution); moat = repayment data loop; constrained by RBI digital-lending rules. AI core but contested (Navi, Piramal).",
        "RevGrowthCeiling": "India consumer digital credit growing fast; ceiling high.",
        "GrowthCatalysts": "Borrower base expansion; repeat-lending frequency; merchant credit; co-lending partnerships.",
        "StagnationCatalysts": "Credit-cycle defaults; RBI rules (FLDG/DLG caps); funding cost.",
    },
    "KNACK": {
        "AI_Moat": "Woven PP sack manufacturing thin moat; AI neutral.",
        "RevGrowthCeiling": "Steady FMCG/agri packaging demand; ceiling low-moderate.",
        "GrowthCatalysts": "Capacity additions; big-brand contract wins; exports.",
        "StagnationCatalysts": "PP cost; price competition; client in-sourcing.",
    },
    "KRONOX": {
        "AI_Moat": "High-purity chemistry + client qualification = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Niche high-purity fine chemicals, capacity bound; ceiling moderate.",
        "GrowthCatalysts": "Pharma/biotech demand; new molecule additions; export share.",
        "StagnationCatalysts": "Client concentration; raw-material cost; regulatory actions.",
    },
    "KROSS": {
        "AI_Moat": "Forged trailer-axle qualification + safety-critical track record = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Trailer/axle demand tied to freight and logistics growth; ceiling moderate.",
        "GrowthCatalysts": "Trailer industry expansion; axle localisation preference; exports.",
        "StagnationCatalysts": "CV freight downturns; steel cost; import competition.",
    },
    "KRYSTAL": {
        "AI_Moat": "Sticky IFM contracts via tenders = thin-moderate moat; robotics/AI cleaning is a long-term margin tool, labour model at risk of wage inflation. AI neutral-positive.",
        "RevGrowthCeiling": "India IFM market growing but manpower pass-through margins thin; ceiling moderate.",
        "GrowthCatalysts": "Corporate/infra contract wins; bundled services; tech-led margin mix.",
        "StagnationCatalysts": "Re-tender losses; wage inflation; client cost cuts.",
    },
    "KSHINTL": {
        "AI_Moat": "Winding-wire engineering (#3 India) with transformer/EV-traction qualifications = moderate moat; energy-transition demand tailwind. AI neutral.",
        "RevGrowthCeiling": "India winding-wire market + EV traction extension; ceiling moderate.",
        "GrowthCatalysts": "EV traction-motor wire; grid transformer demand; exports.",
        "StagnationCatalysts": "Copper cost; import competition; auto cycle.",
    },
    "KUSUMGAR": {
        "AI_Moat": "Coated/laminated technical-textile know-how + defence approvals = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Niche technical textiles; ceiling moderate.",
        "GrowthCatalysts": "Defence fabric orders; industrial applications; new product development.",
        "StagnationCatalysts": "Defence order lumpiness; raw-material cost; competition.",
    },
    "KRN": {
        "AI_Moat": "Heat-exchanger coil scale + OEM qualification = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India AC/refrigerator volume growth; OEM-concentration risk; ceiling moderate-high.",
        "GrowthCatalysts": "AC volume cycle; microchannel efficiency transition; export coils.",
        "StagnationCatalysts": "Weak summers; OEM in-sourcing; copper/aluminium cost.",
    },

    # ---------------- Batch L ----------------
    "LALITHAA": {
        "AI_Moat": "Tier-2/3 South-India jewellery trust brand = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Regional value-jewellery demand; ceiling moderate.",
        "GrowthCatalysts": "Store expansion; gold demand cycle; studded mix.",
        "StagnationCatalysts": "Gold price spikes; Titan/Kalyan competition; regional saturation.",
    },
    "LASERPOWER": {
        "AI_Moat": "Cable/conductor manufacturing + rural EPC = thin-moderate moat; data-centre/grid cable demand an AI-era tailwind.",
        "RevGrowthCeiling": "Grid expansion + electrification programs; ceiling moderate.",
        "GrowthCatalysts": "Power-distribution capex; rural electrification orders; EPC wins.",
        "StagnationCatalysts": "Copper cost; tender competition; receivable cycles.",
    },
    "LAXMIDENTL": {
        "AI_Moat": "Dental lab + aligner brand moat thin-moderate; AI scan/aligner design a tool; D2C aligner rivals (Toothsi) contesting. AI mixed.",
        "RevGrowthCeiling": "Underpenetrated India dental care; ceiling moderate.",
        "GrowthCatalysts": "Clear-aligner adoption; paediatric dentistry; exports.",
        "StagnationCatalysts": "Aligner price competition; dentist-channel dependence; imports.",
    },
    "LAXMIINDIA": {
        "AI_Moat": "Regional MSME underwriting moat moderate; fintech AI credit a mild threat and tool.",
        "RevGrowthCeiling": "Regional MSME credit pool; ceiling moderate.",
        "GrowthCatalysts": "Branch/product expansion; book recovery; funding diversification.",
        "StagnationCatalysts": "Credit cycle; funding cost; NBFC competition.",
    },
    "LCL": {
        "AI_Moat": "Circular-loom machinery niche engineering = moderate moat; automation retrofit an upgrade path. AI neutral.",
        "RevGrowthCeiling": "Woven-sack capacity-addition cycle; ceiling low-moderate.",
        "GrowthCatalysts": "Sack capacity expansions; exports; spares/services recurring stream.",
        "StagnationCatalysts": "Capex-cycle dips; Chinese loom competition.",
    },
    "LGEINDIA": {
        "AI_Moat": "Global brand + premium share + deep distribution = strong moat; AI/smart-home appliance cycle a product tailwind. AI positive.",
        "RevGrowthCeiling": "India consumer durables growing 8-10%; #1 position; ceiling moderate-high.",
        "GrowthCatalysts": "Premiumisation mix; AC/washing penetration; AI-appliance cycle; India exports.",
        "StagnationCatalysts": "Chinese-brand price competition; commodity cost; demand cyclicality.",
    },
    "LEAPIND": {
        "AI_Moat": "Pallet-pooling reverse-logistics density = moderate first-mover network moat; AI asset-tracking marginal. AI neutral.",
        "RevGrowthCeiling": "India pallet pooling nascent, growing with modern logistics; ceiling moderate-high.",
        "GrowthCatalysts": "Client adds; pool density economics; crate/forklift expansion.",
        "StagnationCatalysts": "Logistics slowdown; asset leakage/breakage cost; client in-house pooling.",
    },
    "LENSKART": {
        "AI_Moat": "Vertical integration (own frames, lenses) + omnichannel scale = strong moat; AI home eye-tests/virtual try-on a genuine product edge. AI tailwind.",
        "RevGrowthCeiling": "India eyewear deeply underpenetrated; ceiling high.",
        "GrowthCatalysts": "Store expansion; vision-correction penetration; SE Asia international; premium brands.",
        "StagnationCatalysts": "Online-only rivals; eye-test regulation; store economics in downturns.",
    },
    "LOTUSDEV": {
        "AI_Moat": "Mumbai western-suburbs land + luxury brand = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Launch pipeline bound; ceiling moderate.",
        "GrowthCatalysts": "Luxury housing cycle; redevelopment/JV deals.",
        "StagnationCatalysts": "Approval delays; market downturn; execution risk.",
    },

    # ---------------- Stragglers G/I ----------------
    "IRMENERGY": {
        "AI_Moat": "Exclusive city-gas licences + pipeline infrastructure = regulated local-monopoly moat, strong; AI neutral. EV transition erodes CNG long-term.",
        "RevGrowthCeiling": "CNG/PNG penetration within licence areas; ceiling moderate.",
        "GrowthCatalysts": "CNG vehicle conversions; industrial PNG connections; licence-area expansion.",
        "StagnationCatalysts": "EV adoption in licence geographies; APM gas allocation policy; gas pricing disputes.",
    },
    "GAUDIUMIVF": {
        "AI_Moat": "IVF specialist brand + success-rate reputation = moderate moat; AI embryo-selection improves outcomes (tool). Rising infertility structural demand. AI neutral-positive.",
        "RevGrowthCeiling": "India IVF market growing ~15-20%; hub-spoke reach; ceiling moderate-high.",
        "GrowthCatalysts": "New centres; success-rate brand premium; fertility-preservation services.",
        "StagnationCatalysts": "Specialist doctor dependence; Indira IVF/Nova chain competition; pricing pressure.",
    },

    # ---------------- Batch M ----------------
    "MAMATA": {
        "AI_Moat": "Packaging-machine engineering + export installed base + spares/services = moderate moat; automation/AI-driven machine evolution keeps product relevant. AI neutral-positive.",
        "RevGrowthCeiling": "Global FFS machine demand steady with pharma/FMCG capex; ceiling moderate.",
        "GrowthCatalysts": "Pharma/FMCG packaging capex; export orders; recurring spares/services.",
        "StagnationCatalysts": "Capex cycles; European/Chinese machine competition.",
    },
    "MANBA": {
        "AI_Moat": "Used-2W/3W financing underwriting + 1,118-dealer network = moderate moat; AI credit-scoring a tool, fintech threat mild.",
        "RevGrowthCeiling": "Used-vehicle finance pool growing; ceiling moderate.",
        "GrowthCatalysts": "Dealer network depth; branch additions; asset-quality discipline.",
        "StagnationCatalysts": "Credit cycles; EV residual-value disruption of collateral; funding cost.",
    },
    "MANKIND": {
        "AI_Moat": "Trade-generic brand + chemist distribution moat strong; AI neutral.",
        "RevGrowthCeiling": "India pharma ~10% grower with brand portfolio depth; ceiling moderate-high.",
        "GrowthCatalysts": "Brand portfolio expansion; new launches; expansion markets.",
        "StagnationCatalysts": "NLEM price control; trade-margin regulation; API input cost.",
    },
    "MANIPALHOS": {
        "AI_Moat": "National hospital brand + doctor roster + bed capacity = strong moat; AI diagnostics/operations a margin lever. AI positive.",
        "RevGrowthCeiling": "Structural hospital demand (insurance penetration, Ayushman); ceiling high.",
        "GrowthCatalysts": "Occupancy/ARPOB growth; brownfield bed adds; new hospital ramp; medical value travel.",
        "StagnationCatalysts": "Doctor cost inflation; capex drag; pricing regulation.",
    },
    "MBEL": {
        "AI_Moat": "PEB design-build with in-house fabrication = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India PEB double-digit growth; ceiling moderate-high.",
        "GrowthCatalysts": "Warehouse/industrial construction cycle; export orders.",
        "StagnationCatalysts": "Steel cost; PEB competition; industrial capex pauses.",
    },
    "MEESHO": {
        "AI_Moat": "Value-commerce network effects (sellers x tier-2/3 buyers) + own logistics (Valmo) = moderate-strong moat; AI listing/recommendation tools lower seller friction - tailwind. Quick-commerce adjacency the real threat.",
        "RevGrowthCeiling": "India e-commerce growing 15-20%, value segment largest; ceiling high.",
        "GrowthCatalysts": "Next-200mn user adds; advertising monetisation; logistics cost advantage.",
        "StagnationCatalysts": "Flipkart/Amazon price wars; quick-commerce category creep; e-commerce regulation.",
    },
    "MEDIASSIST": {
        "AI_Moat": "Two-sided TPA network (insurers x hospitals) = moderate-strong moat; AI claims automation a big margin lever, but also eases insurer in-housing - incumbency defends. AI net positive tool.",
        "RevGrowthCeiling": "Health-premium pool growing 15-20% drives claim volumes; TPA fee caps; ceiling moderate-high.",
        "GrowthCatalysts": "Insured-population growth; claim volume scaling; wellness/value-added services.",
        "StagnationCatalysts": "Insurers in-housing claims via AI; TPA fee regulation; fraud spikes.",
    },
    "MEIL": {
        "AI_Moat": "CRGO core processing + transformer-component qualification = moderate moat; grid + AI data-centre transformer supercycle demand. AI tailwind.",
        "RevGrowthCeiling": "Transformer demand cycle, capacity bound; ceiling moderate.",
        "GrowthCatalysts": "Grid expansion; transformer OEM demand; amorphous-core efficiency shift.",
        "StagnationCatalysts": "CRGO steel supply/cost; OEM in-sourcing; import competition.",
    },
    "MIDWESTLTD": {
        "AI_Moat": "Black Galaxy granite quarry reserves + processing = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Export stone demand cycle; ceiling moderate.",
        "GrowthCatalysts": "Engineered stone lines; diamond-tool abrasives; export markets.",
        "StagnationCatalysts": "Construction cycles; freight cost; quartz dumping.",
    },
    "MILKYMIST": {
        "AI_Moat": "Value-added dairy brand + cold-chain distribution = moderate moat; AI neutral (physical product).",
        "RevGrowthCeiling": "VAD dairy growing 12-15% regionally; ceiling moderate.",
        "GrowthCatalysts": "Product portfolio (paneer, ghee); geographic reach; modern trade.",
        "StagnationCatalysts": "Milk procurement cost; Amud/co-op competition; cold-chain economics.",
    },
    "MOLBIO": {
        "AI_Moat": "Truenat device+chip razor-blade platform embedded in national TB programs = strong niche moat; AI diagnostic software an extension. AI positive-ish.",
        "RevGrowthCeiling": "Point-of-care molecular testing growing globally; ceiling moderate-high.",
        "GrowthCatalysts": "TB program volumes; new disease panels; private adoption; exports.",
        "StagnationCatalysts": "Global Fund/donor funding cycles; Cepheid competition; tender pricing.",
    },
    "MOTISONS": {
        "AI_Moat": "Jaipur jewellery trust brand = moderate local moat; AI neutral.",
        "RevGrowthCeiling": "Regional jewellery demand; ceiling moderate-low.",
        "GrowthCatalysts": "Showroom additions; wedding-season demand; coin/utensil mix.",
        "StagnationCatalysts": "Gold price spikes; competition; Jaipur concentration.",
    },
    "MOBIKWIK": {
        "AI_Moat": "Wallet moat eroded by UPI; remaining edge = credit distribution data; AI underwriting a tool. AI neutral; UPI zero-MDR economics structural squeeze.",
        "RevGrowthCeiling": "Payments fee pool compressed; credit distribution the growth leg; ceiling moderate.",
        "GrowthCatalysts": "ZiperMC credit growth; Soundbox; bill-pay commissions.",
        "StagnationCatalysts": "PhonePe/GPay dominance; RBI digital-credit rules; wallet disintermediation.",
    },
    "MUKKA": {
        "AI_Moat": "Fish-landing access + processing scale = moderate regional moat; AI neutral.",
        "RevGrowthCeiling": "Genuinely resource-capped (fish catch); ceiling low-moderate.",
        "GrowthCatalysts": "Aquaculture feed demand; processing capacity; exports.",
        "StagnationCatalysts": "Catch variability (monsoon/El Nino); shrimp export cycles; sustainability rules.",
    },
    "MUTHOOTMF": {
        "AI_Moat": "JLG microfinance with Muthoot brand = moderate moat; AI credit-scoring a tool; credit-cycle risk the real variable.",
        "RevGrowthCeiling": "MFI market Rs 4-5 lakh cr; ceiling high-ish.",
        "GrowthCatalysts": "Branch expansion; borrower base; product adjacencies.",
        "StagnationCatalysts": "MFI stress events (Assam-type); microfinance regulation; competition.",
    },
    "MUFTI": {
        "AI_Moat": "MUFTI menswear brand moat moderate (niche casual); AI fashion-design tools marginal. AI neutral.",
        "RevGrowthCeiling": "Menswear growing 8-10%; niche brand; ceiling moderate.",
        "GrowthCatalysts": "Exclusive-store expansion; online share; premium-casual trend.",
        "StagnationCatalysts": "Fast-fashion competition; department-store weakness; fashion-cycle misses.",
    },
    "MVELECTRO": {
        "AI_Moat": "Railway propulsion (IGBT) with RDSO/safety qualifications = strong niche moat, slow to displace; rail electrification structural. AI neutral.",
        "RevGrowthCeiling": "Indian Railways capex cycle (Vande Bharat-type programs); ceiling moderate-high.",
        "GrowthCatalysts": "Loco/EMU propulsion orders; Vande Bharat programs; metro orders; exports.",
        "StagnationCatalysts": "Railway order timing; RDSO approval delays; Siemens/ABB competition.",
    },
    "MVGJL": {
        "AI_Moat": "Vaibhav Jewellers AP/Telangana trust brand = moderate regional moat; AI neutral.",
        "RevGrowthCeiling": "Regional jewellery demand; ceiling moderate.",
        "GrowthCatalysts": "Store expansion; wedding gold demand; studded mix.",
        "StagnationCatalysts": "Gold price spikes; Titan/Kalyan expansion; regional saturation.",
    },

    # ---------------- Batch N ----------------
    "NETWEB": {
        "AI_Moat": "AI is the demand: OEM partnerships (NVIDIA-class) + system-integration capability for GPU servers; risks commoditisation as market matures. Domestic AI-infrastructure policy tailwind.",
        "RevGrowthCeiling": "India AI infra capex just starting (sovereign GPU missions, datacentres); ceiling high over the cycle.",
        "GrowthCatalysts": "GPU server orders; datacentre buildouts; sovereign AI projects; managed services.",
        "StagnationCatalysts": "Global AI capex digestion; Dell/Supermicro competition; import/policy dependence; thin margins.",
    },
    "NIVABUPA": {
        "AI_Moat": "Health-insurance brand + hospital network + claims infrastructure = moderate-strong moat; AI underwriting/claims a margin lever. AI positive.",
        "RevGrowthCeiling": "Health insurance growing 15-20% (low penetration); ceiling high.",
        "GrowthCatalysts": "Retail health policy growth; premium inflation; digital distribution.",
        "StagnationCatalysts": "Medical-inflation loss ratios; Star/HDFC Ergo competition; IRDAI pricing rules.",
    },
    "NORTHARC": {
        "AI_Moat": "Multi-product small-borrower lender (micro, consumer, vehicle) moderate moat; AI credit tools table stakes.",
        "RevGrowthCeiling": "MFI + consumer credit pools large; ceiling moderate-high.",
        "GrowthCatalysts": "Branch expansion; product mix; portfolio quality repair.",
        "StagnationCatalysts": "Credit-cycle stress; regulation; funding cost.",
    },
    "NOVAAGRI": {
        "AI_Moat": "Bio-input products + dealer network = thin-moderate moat; organic-farming trend tailwind. AI neutral.",
        "RevGrowthCeiling": "Organic/bio-input niche small but growing; ceiling low-moderate.",
        "GrowthCatalysts": "Organic adoption; government bio-agriculture programs; exports.",
        "StagnationCatalysts": "Subsidy dependence; chemical-input yield advantage; farmer adoption friction.",
    },
    "NEPHROPLUS": {
        "AI_Moat": "Largest dialysis network + standardised protocols + hospital PPP/captive contracts = moderate-strong moat; chronic kidney disease rising structurally. AI neutral.",
        "RevGrowthCeiling": "India dialysis demand huge, penetration low; ceiling high.",
        "GrowthCatalysts": "New centres; hospital-captive contracts; tier-2/3 expansion; transplant services.",
        "StagnationCatalysts": "Government program reimbursement rates; nephrologist shortage; consumable import cost.",
    },
    "NTPCGREEN": {
        "AI_Moat": "Sovereign-backed renewable IPP (NTPC balance sheet) = strongest funding moat in sector; AI data-centre power demand tailwind. AI-proof asset moat.",
        "RevGrowthCeiling": "Group pipeline 60 GW+; ceiling high.",
        "GrowthCatalysts": "Capacity commissioning; C&I green offtake; green-hydrogen projects.",
        "StagnationCatalysts": "Tariff competition; execution slippage; curtailment/discom offtake issues.",
    },

    # ---------------- Batch O ----------------
    "OLAELEC": {
        "AI_Moat": "Claims vertical integration (cells, software, AI stack) but moat weak vs incumbent OEM scale; quality/service perception damage. AI central to product yet hasn't protected share.",
        "RevGrowthCeiling": "EV 2W market growing fast; company share volatile; ceiling high only if execution fixed.",
        "GrowthCatalysts": "New model launches; cell gigafactory scale; distribution expansion.",
        "StagnationCatalysts": "Quality/recall reputational drag; price war; cash burn; TVS/Bajaj EV push.",
    },
    "OMFREIGHT": {
        "AI_Moat": "Multimodal 3PL + customs relationships = moderate moat; AI freight platforms compress brokerage margins - mild threat.",
        "RevGrowthCeiling": "EXIM logistics growing with trade; ceiling moderate.",
        "GrowthCatalysts": "EXIM trade volumes; contract logistics wins; multimodal mix.",
        "StagnationCatalysts": "Global trade slowdowns; freight-rate crashes; margin thinness.",
    },
    "OMNI": {
        "AI_Moat": "High-precision engineered components with global qualification = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "Order-book bound; global industrial demand; ceiling moderate.",
        "GrowthCatalysts": "Export order ramp; capacity adds; new verticals.",
        "StagnationCatalysts": "Global industrial cycles; raw-material cost; competition.",
    },
    "OMPOWER": {
        "AI_Moat": "Power T&D EPC execution moat moderate; grid capex golden cycle (incl AI-datacentre load) tailwind. AI neutral-positive.",
        "RevGrowthCeiling": "Transmission capex upcycle; ceiling moderate-high.",
        "GrowthCatalysts": "HV/EHV line awards; substation orders; underground cabling programs.",
        "StagnationCatalysts": "Receivable cycles; Kalpataru/Torrent competition; commodity cost.",
    },
    "ORKLAINDIA": {
        "AI_Moat": "Heritage brands (MTR, Eastern) + distribution = strong moat; AI neutral.",
        "RevGrowthCeiling": "Packaged foods/spice mixes ~10% grower; ceiling moderate-high.",
        "GrowthCatalysts": "Category expansion; distribution depth; NRI exports.",
        "StagnationCatalysts": "Raw-material inflation; regional competition; FSSAI regulation.",
    },
    "ORIENTTECH": {
        "AI_Moat": "IT reseller-to-services moat thin; AI/cloud shift forces service pivot; hyperscaler direct sales a threat. AI threat and tool.",
        "RevGrowthCeiling": "India IT spend growing; ceiling moderate.",
        "GrowthCatalysts": "Datacentre/cloud services; managed services; government contracts.",
        "StagnationCatalysts": "Hardware margin compression; cloud cannibalising on-prem; competition.",
    },
    "OSWALPUMPS": {
        "AI_Moat": "Pump manufacturing + solar-pump engineering with export network = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Domestic solar-pump programs + export markets; ceiling moderate.",
        "GrowthCatalysts": "PM-KUSUM demand; US/export distributor expansion; capacity.",
        "StagnationCatalysts": "Subsidy budget dependence; US tariffs; competition.",
    },

    # ---------------- Batch P ----------------
    "PACEDIGITK": {
        "AI_Moat": "Telecom DC-power install base + solar equipment = moderate moat; AI neutral. 5G/network power demand steady.",
        "RevGrowthCeiling": "Telecom + solar capex cycle bound; ceiling moderate.",
        "GrowthCatalysts": "5G rollouts; solar plant equipment; service attach.",
        "StagnationCatalysts": "Operator capex pauses; competition; import cost.",
    },
    "PARKHOTELS": {
        "AI_Moat": "Upscale Park brand + Flurys heritage + owned assets = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "Occupancy x rate cycle; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; new hotels; Flurys retail expansion.",
        "StagnationCatalysts": "Travel shocks; renovation capex; leverage.",
    },
    "PARKHOSPS": {
        "AI_Moat": "North-India NABH hospital brand + 4,000 beds = moderate-strong moat; AI operations a margin lever. AI positive.",
        "RevGrowthCeiling": "Regional healthcare demand structural; ceiling high-ish.",
        "GrowthCatalysts": "Occupancy/ARPOB growth; bed additions; insurance penetration.",
        "StagnationCatalysts": "Doctor cost inflation; capex drag; competition.",
    },
    "PATELRMART": {
        "AI_Moat": "Value-grocery supermarket moat thin; AI inventory tools marginal. AI neutral.",
        "RevGrowthCeiling": "Regional supermarket expansion; DMart/quick-commerce squeeze; ceiling low-moderate.",
        "GrowthCatalysts": "Store additions; private-label mix; supply-chain efficiency.",
        "StagnationCatalysts": "DMart scale competition; quick commerce; thin grocery margins.",
    },
    "PINELABS": {
        "AI_Moat": "Two-sided merchant network (POS, issuing, processing) = moderate-strong moat; UPI/QR margin pressure real, soundbox/merchant-credit extends. AI neutral; digital-payments secular.",
        "RevGrowthCeiling": "India digital payments growing 20%+; ceiling high.",
        "GrowthCatalysts": "POS/soundbox attach; merchant lending; gift-card issuing scale.",
        "StagnationCatalysts": "UPI/QR displacing POS margins; PhonePe/Jio pricing; RBI fee regulation.",
    },
    "PLATIND": {
        "AI_Moat": "PVC-stabiliser specialty chemistry + #3 India share = moderate moat; AI neutral.",
        "RevGrowthCeiling": "PVC pipe/construction demand growth; ceiling moderate.",
        "GrowthCatalysts": "CPVC additive growth; pipe demand; exports.",
        "StagnationCatalysts": "PVC resin cycles; lead-stabiliser regulation; import competition.",
    },
    "PLAZACABLE": {
        "AI_Moat": "Wires brand + FMEG distribution = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India wires growing with housing/electrification; ceiling moderate.",
        "GrowthCatalysts": "FMEG portfolio expansion; distribution depth; exports.",
        "StagnationCatalysts": "Copper cost; RR Kabel/Havells/Polycab competition; demand cyclicality.",
    },
    "POWERICA": {
        "AI_Moat": "40-year Cummins OEM tie-up = strong relationship moat; AI data-centre backup-power demand a tailwind. AI positive.",
        "RevGrowthCeiling": "Genset demand cyclical (industrial/infra) + datacentre extension; ceiling moderate.",
        "GrowthCatalysts": "Datacentre gensets; industrial capex; exports; marine power.",
        "StagnationCatalysts": "Industrial slowdown; genset-to-BESS substitution long-term; Cummins policy shifts.",
    },
    "PREMIERENE": {
        "AI_Moat": "Integrated cell+module scale with ALMM protection = moderate moat; AI data-centre energy demand tailwind; pricing commodity-cyclical.",
        "RevGrowthCeiling": "India solar additions growing to 500 GW target; ceiling high but price-cyclical.",
        "GrowthCatalysts": "Capacity expansion; cell integration margin; exports.",
        "StagnationCatalysts": "Chinese overcapacity price crashes; ALMM/duty policy shifts; raw-material cost.",
    },
    "PROSTARM": {
        "AI_Moat": "UPS/inverter brand + channel = moderate moat; AI neutral. Datacentre UPS demand incremental.",
        "RevGrowthCeiling": "Power-backup market growing steadily; ceiling moderate.",
        "GrowthCatalysts": "Solar hybrid inverters; lithium battery packs; datacentre UPS.",
        "StagnationCatalysts": "Luminous/Microtek competition; lithium import cost; price wars.",
    },
    "PWL": {
        "AI_Moat": "AI tutoring threatens content-led test prep, but PW's low-cost structure + mass brand defend; AI content generation cuts costs further. AI mixed - threat to premium rivals, tool for PW.",
        "RevGrowthCeiling": "Test-prep market large, online shift ongoing; ceiling moderate-high.",
        "GrowthCatalysts": "JEE/NEET enrolments; offline Vidyapeeth centres; UPSC/upskilling expansion.",
        "StagnationCatalysts": "Enrolment cyclicality; AI-native free rivals; coaching regulation.",
    },
    "PYRAMID": {
        "AI_Moat": "Polymer packaging (drums, IBC) manufacturing = thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "Agrochem/lubricant packaging demand; ceiling moderate.",
        "GrowthCatalysts": "IBC container share; capacity adds; exports.",
        "StagnationCatalysts": "Polymer cost; price competition; client in-sourcing.",
    },
    "PVSL": {
        "AI_Moat": "Maruti dealership territory + brand = moderate moat; EV agency-model transition a structural risk. AI neutral.",
        "RevGrowthCeiling": "Tied to Maruti volumes in territory; ceiling low-moderate.",
        "GrowthCatalysts": "Dealership additions; high-margin service mix; insurance/finance commissions.",
        "StagnationCatalysts": "Maruti share erosion; EV distribution model shifts; OEM margin squeeze.",
    },
    "PNGJL": {
        "AI_Moat": "1832-heritage Maharashtra jewellery trust brand = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Maharashtra gold demand; ceiling moderate.",
        "GrowthCatalysts": "Store expansion; wedding demand; studded mix.",
        "StagnationCatalysts": "Gold price spikes; competition; regional concentration.",
    },
    "PNGSREVA": {
        "AI_Moat": "Studded-jewellery (Reva) brand + store network = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Studded-jewellery penetration rising with income; ceiling moderate.",
        "GrowthCatalysts": "Store additions; diamond-studded demand; online channel.",
        "StagnationCatalysts": "Diamond demand cycles; gold cost; competition.",
    },

    # ---------------- Batch Q ----------------
    "QPOWER": {
        "AI_Moat": "HV busbar/switchgear qualification + AI data-centre electrical gear demand supercycle = tailwind; moat moderate.",
        "RevGrowthCeiling": "India transmission + datacentre electrical demand growing fast; ceiling moderate-high.",
        "GrowthCatalysts": "Datacentre busbar/switchgear orders; grid capex; capacity expansion.",
        "StagnationCatalysts": "Execution scale-up; Schneider/L&T competition; copper cost.",
    },
    "QUADFUTURE": {
        "AI_Moat": "KAVACH rail-safety certification + speciality rail/defence cable qualifications = strong niche moat. AI neutral.",
        "RevGrowthCeiling": "Railways modernisation (KAVACH rollout, Vande Bharat) pipeline; ceiling moderate-high.",
        "GrowthCatalysts": "KAVACH orders; defence cable demand; EV charging cables.",
        "StagnationCatalysts": "Railway order timing; certification delays; competition.",
    },

    # ---------------- Batch R ----------------
    "RAJPUTANA": {
        "AI_Moat": "Biodiesel feedstock sourcing + OMC blending relationships = policy-dependent moderate moat; AI neutral.",
        "RevGrowthCeiling": "Blending-mandate targets + feedstock availability cap; ceiling moderate.",
        "GrowthCatalysts": "Blending mandate increases; capacity expansion; glycerine by-product value.",
        "StagnationCatalysts": "UCO feedstock cost/availability; blending policy changes; imports.",
    },
    "RAMBHAJO": {
        "AI_Moat": "Kundan/Polki craftsmanship brand = moderate moat; AI design tools marginal. AI neutral.",
        "RevGrowthCeiling": "Occasion-wear jewellery demand; ceiling moderate.",
        "GrowthCatalysts": "Retail expansion; exports; wedding demand.",
        "StagnationCatalysts": "Gold/diamond cost; fashion shifts; artisan dependence.",
    },
    "RATNAVEER": {
        "AI_Moat": "SS fastener processing + solar mounting frames = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Fastener demand + solar-frame attach; ceiling moderate.",
        "GrowthCatalysts": "Solar installation growth; export washers; capacity adds.",
        "StagnationCatalysts": "Steel cost; solar cycle dips; competition.",
    },
    "RBZJEWEL": {
        "AI_Moat": "Heritage antique-jewellery craftsmanship at scale = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Antique-jewellery niche demand; ceiling moderate.",
        "GrowthCatalysts": "Retail expansion; exports; wedding-driven demand.",
        "StagnationCatalysts": "Gold cost; fashion cycles; artisan dependence.",
    },
    "REGAAL": {
        "AI_Moat": "Maize-starch processing scale + derivatives portfolio = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Starch/derivative demand growing with food/paper/pharma; ceiling moderate.",
        "GrowthCatalysts": "Higher-value derivatives mix; capacity; exports.",
        "StagnationCatalysts": "Maize cost; glucose price cycles; competition.",
    },
    "RISHABH": {
        "AI_Moat": "T&M instrument engineering niche (import substitution) = moderate moat; smart-instrument tech incremental. AI neutral.",
        "RevGrowthCeiling": "India T&M market growing with industrialisation; ceiling moderate.",
        "GrowthCatalysts": "Industrial automation demand; exports; new product lines.",
        "StagnationCatalysts": "Chinese instrument competition; industrial capex dips.",
    },
    "RKSWAMY": {
        "AI_Moat": "AI directly threatens conventional ad-market-research (survey automation, AI creative) - must pivot to data-analytics moat; client relationships + data assets defend meanwhile. AI real threat + tool.",
        "RevGrowthCeiling": "India ad spend growing ~10%; ceiling moderate.",
        "GrowthCatalysts": "Digital/analytics mix shift; data-science services; client wallet expansion.",
        "StagnationCatalysts": "AI commoditising research; client in-housing; ad-spend cyclicality.",
    },
    "RPTECH": {
        "AI_Moat": "80+ brand distribution (Apple, Intel) + channel reach = moderate moat; D2C/online shift a slow structural threat. AI neutral.",
        "RevGrowthCeiling": "India IT-device market growing; distribution margins thin; ceiling moderate.",
        "GrowthCatalysts": "Apple premium growth; enterprise IT demand; new brands.",
        "StagnationCatalysts": "D2C channel shift; margin compression; inventory cycles.",
    },
    "RRKABEL": {
        "AI_Moat": "Wire brand + distribution + export base = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "India wires/cables double-digit growth (housing, infra); ceiling moderate-high.",
        "GrowthCatalysts": "FMEG portfolio (fans, lights, switches); exports; capacity.",
        "StagnationCatalysts": "Copper cost; Havells/Polycab competition; demand cyclicality.",
    },
    "ROSSTECH": {
        "AI_Moat": "Defence/aerospace harness qualification + engineering services = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "Defence localisation pipeline, order-book bound; ceiling moderate.",
        "GrowthCatalysts": "Defence orders; commercial aviation/MRO; engineering-services share.",
        "StagnationCatalysts": "Program delays; qualification timelines; competition.",
    },
    "RSL": {
        "AI_Moat": "Commodity steel long products - no meaningful moat; AI neutral.",
        "RevGrowthCeiling": "Steel demand cycle bound; ceiling low-moderate.",
        "GrowthCatalysts": "Volume growth; capacity utilisation; infrastructure demand.",
        "StagnationCatalysts": "Steel price cycles; imports; raw-material cost.",
    },
    "RUBICON": {
        "AI_Moat": "Difficult-to-copy drug-delivery platforms + complex-generic US filings = moderate-strong moat; AI drug-development speeds pipeline. AI neutral-positive.",
        "RevGrowthCeiling": "US complex-generic niche with better pricing than plain generics; ceiling moderate-high.",
        "GrowthCatalysts": "New complex approvals; pipeline launches; therapeutic expansion.",
        "StagnationCatalysts": "FDA actions; generic price erosion; R&D execution slips.",
    },

    # ---------------- Batch S ----------------
    "SETL": {
        "AI_Moat": "Glass-lining process know-how + pharma-capex qualification = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Pharma/chemical capex cycle; exports ~30% of order book; ceiling moderate.",
        "GrowthCatalysts": "Pharma capacity buildout; lifecycle services/spares; export share.",
        "StagnationCatalysts": "Capex pauses; competition; execution slippage.",
    },
    "STYL": {
        "AI_Moat": "Secure-print certifications + bank relationships durable, but UPI/e-cheque digitisation structurally shrinks print volumes - digital a long-term negative; pivot to card personalisation/digital security needed.",
        "RevGrowthCeiling": "Card issuance growing while cheques decline; blended ceiling moderate-low.",
        "GrowthCatalysts": "Debit/credit card issuance volumes; metal-card premium; new secure products.",
        "StagnationCatalysts": "UPI displacing card usage; cheque phase-out; digital-first issuance.",
    },
    "SAILIFE": {
        "AI_Moat": "CRDMO chemistry + biologics with global client lock-ins = moderate-strong moat; AI drug-design feeds CDMO pipeline - tailwind.",
        "RevGrowthCeiling": "Global CDMO shift to India structural; ceiling high.",
        "GrowthCatalysts": "CDMO order book; biologics capacity; specialty molecules.",
        "StagnationCatalysts": "Global pharma capex cycles; pricing; biosecurity geopolitics.",
    },
    "SENORES": {
        "AI_Moat": "Regulated-market niche generics + specialty filings = moderate moat; AI neutral.",
        "RevGrowthCeiling": "US generics price-eroded; emerging-market angle extends; ceiling moderate.",
        "GrowthCatalysts": "US filings pipeline; emerging-market expansion; specialty approvals.",
        "StagnationCatalysts": "US price erosion; FDA actions; API input cost.",
    },
    "SHREEJISPG": {
        "AI_Moat": "Dry-bulk shipping - cyclical asset business, no durable moat; AI neutral.",
        "RevGrowthCeiling": "Freight-rate cycle bound; ceiling low-moderate.",
        "GrowthCatalysts": "Freight-rate upcycles; fleet additions; India/Sri Lanka cargo demand.",
        "StagnationCatalysts": "Freight crashes; fuel cost; industry oversupply.",
    },
    "STALLION": {
        "AI_Moat": "Refrigerant/industrial-gas blending with OEM/industry relationships = moderate regional moat; AI neutral.",
        "RevGrowthCeiling": "AC refrigerant + industrial gas demand; ceiling moderate.",
        "GrowthCatalysts": "AC/output demand; industrial gas volume; capacity adds.",
        "StagnationCatalysts": "HFC phase-down regulation (Kigali); feedstock cost; competition.",
    },
    "SURAKSHA": {
        "AI_Moat": "Regional diagnostics brand + hub-and-spoke = thin-moderate moat; AI reporting a cost lever but enables national AI-powered rivals too. AI mixed.",
        "RevGrowthCeiling": "East-India diagnostics penetration; ceiling moderate.",
        "GrowthCatalysts": "Test volume growth; home collection; centre expansion.",
        "StagnationCatalysts": "National-chain price competition; AI tele-reporting rivals; regulated test pricing.",
    },
    "SMARTWORKS": {
        "AI_Moat": "Enterprise managed-office relationships + fit-out scale = moderate moat; hybrid-work era demand tailwind. AI positive for flex demand.",
        "RevGrowthCeiling": "Institutional flex demand growing; ceiling moderate-high.",
        "GrowthCatalysts": "Campus/seat additions; enterprise pre-commits; utilisation gains.",
        "StagnationCatalysts": "IT-sector headcount freezes; lease-commitment rigidity; Awfis/IndiQube competition.",
    },
    "SANSTAR": {
        "AI_Moat": "Maize specialty-ingredient processing scale = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Starch/glucose/dextrose demand growing with food/pharma; ceiling moderate.",
        "GrowthCatalysts": "Derivatives mix; capacity; exports.",
        "StagnationCatalysts": "Maize cost; price cycles; competition.",
    },
    "SAMBHV": {
        "AI_Moat": "ERW steel pipes thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "Pipe demand (water, O&G, structural) cycle; ceiling moderate.",
        "GrowthCatalysts": "Capacity expansion; export orders; infrastructure demand.",
        "StagnationCatalysts": "Steel cycles; import competition; margin thinness.",
    },
    "SAATVIKGL": {
        "AI_Moat": "4.86 GW module scale with ALMM protection = moderate moat; AI data-centre energy demand tailwind; commodity-pricing cyclical.",
        "RevGrowthCeiling": "India solar additions rising; ceiling high but price-cyclical.",
        "GrowthCatalysts": "Capacity expansion; EPC/O&M attach; exports.",
        "StagnationCatalysts": "Chinese price wars; policy shifts; raw-material cost.",
    },
    "SANATHAN": {
        "AI_Moat": "Commodity yarn manufacturer thin moat; technical-yarn mix improves slightly. AI neutral.",
        "RevGrowthCeiling": "Yarn demand cycle; ceiling low-moderate.",
        "GrowthCatalysts": "Technical-textile yarn mix; capacity; export recovery.",
        "StagnationCatalysts": "PET/cotton cost; power cost; competition.",
    },
    "SENCO": {
        "AI_Moat": "Eastern-India organised jewellery brand (Senco Gold) = moderate moat; AI neutral.",
        "RevGrowthCeiling": "East-India demand + franchise-led expansion; ceiling moderate.",
        "GrowthCatalysts": "Franchise store adds; studded/diamond mix; light-weight designs.",
        "StagnationCatalysts": "Gold price spikes; Titan/regional competition; regional concentration.",
    },
    "SRM": {
        "AI_Moat": "Hill-terrain road/tunnel execution specialisation (J&K, Ladakh, Uttarakhand) = moderate niche moat; AI neutral.",
        "RevGrowthCeiling": "Border/hill infra pipeline (strategic roads, tunnels); ceiling moderate.",
        "GrowthCatalysts": "Tunnel/slope-stabilisation awards; execution track; order-book build.",
        "StagnationCatalysts": "Govt receivables; terrain/geological risk; tender aggression.",
    },
    "SAGILITY": {
        "AI_Moat": "High AI-disruption exposure: GenAI automates claims/provider back-office - the core service; moat = US payer/provider relationships + healthcare domain; must pivot AI-first or pricing compresses. AI threat + opportunity.",
        "RevGrowthCeiling": "US healthcare admin outsourcing TAM large; ceiling high if AI pivot lands.",
        "GrowthCatalysts": "Payer outsourcing share; AI-embedded margin expansion; new service lines.",
        "StagnationCatalysts": "AI automation commoditising BPO pricing; client in-housing; US healthcare policy.",
    },
    "SHANTIGOLD": {
        "AI_Moat": "22KT daily-wear jewellery brand = moderate local moat; AI neutral.",
        "RevGrowthCeiling": "Regional jewellery demand; ceiling moderate.",
        "GrowthCatalysts": "Retail/online expansion; bridal and festive demand.",
        "StagnationCatalysts": "Gold cost; competition; regional concentration.",
    },
    "SBFC": {
        "AI_Moat": "Secured MSME + gold-loan underwriting with branch network = moderate moat; AI credit tools table stakes.",
        "RevGrowthCeiling": "Secured MSME credit pool large; ceiling high-ish.",
        "GrowthCatalysts": "AUM growth 25%+; branch expansion; gold-loan mix.",
        "StagnationCatalysts": "Credit-cycle stress; competition; funding cost.",
    },
    "SSDL": {
        "AI_Moat": "B2B saree wholesale from 900+ weavers = thin distribution moat; AI neutral.",
        "RevGrowthCeiling": "Saree trade mature/declining; ceiling low.",
        "GrowthCatalysts": "Weaver network depth; retailer additions; apparel mix.",
        "StagnationCatalysts": "Saree demand erosion; retailer credit risk; e-commerce disintermediation.",
    },
    "SHRINGARMS": {
        "AI_Moat": "Mangalsutra manufacturing niche (B2B) = thin-moderate moat; ritual demand stable. AI neutral.",
        "RevGrowthCeiling": "Mangalsutra demand steady-ritual; ceiling moderate.",
        "GrowthCatalysts": "B2B client additions; capacity; retail-brand extension.",
        "StagnationCatalysts": "Gold cost; client concentration; B2B margin thinness.",
    },
    "SWIGGY": {
        "AI_Moat": "Duopoly network effects (riders x restaurants x users) + Instamart dark-store logistics = strong moat; AI demand forecasting/routing a margin lever. AI positive; Zomato rivalry the real contest.",
        "RevGrowthCeiling": "Food delivery 15-20% growth; quick-commerce exploding; ceiling high.",
        "GrowthCatalysts": "Instamart order growth; food-delivery AOV/ads; Swiggy One subscriptions.",
        "StagnationCatalysts": "Zomato/Blinkit burn wars; quick-commerce margin pressure; gig-labour regulation.",
    },
    "SAMHI": {
        "AI_Moat": "Owned hotel assets under Marriott/Hyatt/IHG management = asset moat; AI neutral.",
        "RevGrowthCeiling": "Occupancy x rate cycle; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; new hotels; renovation-led repositioning.",
        "StagnationCatalysts": "Travel shocks; leverage; capex cycles.",
    },
    "SURAJEST": {
        "AI_Moat": "South-Mumbai redevelopment land relationships = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Redevelopment pipeline bound; ceiling moderate.",
        "GrowthCatalysts": "Redevelopment society wins; ultra-luxury launches; business-park builds.",
        "StagnationCatalysts": "Approval delays; Mumbai luxury cycle; execution slippage.",
    },
    "SCODATUBES": {
        "AI_Moat": "SS seamless pipe manufacturing niche = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Oil&gas/pharma SS pipe demand; ceiling moderate.",
        "GrowthCatalysts": "Capacity adds; export grades; new industries.",
        "StagnationCatalysts": "Steel cost; import competition; capex cycles.",
    },
    "SOLARWORLD": {
        "AI_Moat": "Solar EPC + module manufacturing thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "Solar install volumes growing; price competition caps; ceiling moderate.",
        "GrowthCatalysts": "EPC order book; module capacity; utility programs.",
        "StagnationCatalysts": "Price wars; policy shifts; execution margin risk.",
    },
    "STUDDS": {
        "AI_Moat": "Studds mass + SMK premium brand with manufacturing scale = moderate-strong moat in helmets; mandate enforcement drives organised share. AI neutral.",
        "RevGrowthCeiling": "Helmet market growing with 2W volumes + premiumisation + exports; ceiling moderate.",
        "GrowthCatalysts": "Premium SMK mix; exports; enforcement-driven organised share shift.",
        "StagnationCatalysts": "2W demand dips; unorganised cheap competition; input cost.",
    },
    "SIGNATURE": {
        "AI_Moat": "Gurugram/NCR mid-housing brand + land bank = moderate moat; AI neutral.",
        "RevGrowthCeiling": "NCR housing revival + guided pipeline; ceiling moderate-high.",
        "GrowthCatalysts": "Launch velocity; premiumisation mix; NCR demand revival.",
        "StagnationCatalysts": "NCR property downturn; approvals; leverage.",
    },
    "STANLEY": {
        "AI_Moat": "Luxury furniture brand + showroom experience (Stanley/Otto) = moderate moat vs imported luxury; AI neutral.",
        "RevGrowthCeiling": "India luxury-furniture niche rising with HNI wealth; ceiling moderate.",
        "GrowthCatalysts": "Showroom expansion; premiumisation; import substitution.",
        "StagnationCatalysts": "Discretionary demand downturns; leather import cost; imported-brand competition.",
    },
    "SAIPARENT": {
        "AI_Moat": "Injectable/oral formulations with regulated approvals = moderate moat; AI neutral.",
        "RevGrowthCeiling": "India + export formulation demand; ceiling moderate-high.",
        "GrowthCatalysts": "Injectable capacity; export registrations; cephalosporin niche.",
        "StagnationCatalysts": "Price erosion; regulatory actions; input cost.",
    },
    "SBIFUNDS": {
        "AI_Moat": "India's largest AMC - brand + bank distribution + scale = strong moat; AI robo-advice a mild long-term fee threat. AI neutral near-term.",
        "RevGrowthCeiling": "India MF AUM compounding mid-teens; #1 rides flows; ceiling high.",
        "GrowthCatalysts": "SIP inflows; equity market AUM mark-ups; branch/digital distribution.",
        "StagnationCatalysts": "Bear markets; TER compression; passive shift.",
    },
    "SEDEMAC": {
        "AI_Moat": "Embedded control electronics (ECUs) with long design-in cycles = moderate-strong moat; EV powertrain control and AI-defined vehicles raise software content per vehicle - tailwind.",
        "RevGrowthCeiling": "India ECU content rising across ICE/EV/genset/industrial; ceiling moderate-high.",
        "GrowthCatalysts": "EV controller demand; genset/industrial controls; export design wins.",
        "StagnationCatalysts": "OEM sourcing shifts to global Tier-1s; semiconductor cycles; pricing.",
    },
    "SHADOWFAX": {
        "AI_Moat": "Asset-light crowdsourced rider network + e-commerce integrations = moderate moat; AI routing efficiency; Delhivery/Shiprocket contest. AI neutral-positive.",
        "RevGrowthCeiling": "E-com/quick-commerce logistics volumes growing 20%+; ceiling high-ish.",
        "GrowthCatalysts": "Merchant additions; quick-commerce peak volumes; hyperlocal 3PL wins.",
        "StagnationCatalysts": "Gig-labour regulation; margin thinness; Delhivery scale competition.",
    },
    "SHANKESH": {
        "AI_Moat": "B2B handcrafted jewellery + job-work = thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "B2B jewellery demand; ceiling moderate-low.",
        "GrowthCatalysts": "Client jeweller additions; capacity; customisation.",
        "StagnationCatalysts": "Gold cost volatility; client concentration; margin thinness.",
    },
    "SHIPROCKET": {
        "AI_Moat": "Courier aggregator network + scale pricing for D2C sellers = moderate moat; AI logistics tools incremental; couriers going direct a threat. AI neutral.",
        "RevGrowthCeiling": "D2C e-commerce shipping growing; ceiling moderate-high.",
        "GrowthCatalysts": "Seller additions; fulfilment centres; marketing SaaS attach.",
        "StagnationCatalysts": "Courier partners direct deals; rate competition; seller churn/failure rates.",
    },
    "SRTL": {
        "AI_Moat": "Cotton yarn spinner - commodity, thin moat; AI neutral.",
        "RevGrowthCeiling": "Yarn demand cycle; ceiling low-moderate.",
        "GrowthCatalysts": "Capacity utilisation; cotton spread management; exports.",
        "StagnationCatalysts": "Cotton cost volatility; demand dips; power cost.",
    },
    "SUDEEPPHRM": {
        "AI_Moat": "Specialty excipient + mineral-salt chemistry with pharma qualifications = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Excipient demand growing with pharma volumes; ceiling moderate.",
        "GrowthCatalysts": "Capacity; export registrations; specialty grades.",
        "StagnationCatalysts": "Raw-material cost; competition; pharma capex cycles.",
    },
    "SUNSHINE": {
        "AI_Moat": "Content IP + filmmaker relationships = hit-driven thin moat; AI-generated content disrupts production economics - threat to premium content, also a tool. AI mixed-negative.",
        "RevGrowthCeiling": "Film economics hit-driven, theatrical under pressure; ceiling low-moderate.",
        "GrowthCatalysts": "OTT licensing deals; slate expansion; tentpole successes.",
        "StagnationCatalysts": "Box-office volatility; AI-generated content competition; talent cost inflation.",
    },

    # ---------------- Batch T ----------------
    "TBOTEK": {
        "AI_Moat": "B2B travel platform network effects (suppliers x agents) = moderate-strong moat; AI trip-planning could bypass travel agents - the key watch item; TBO AI tools defend. AI mixed.",
        "RevGrowthCeiling": "B2B travel bookings growing 15-20%; ceiling high.",
        "GrowthCatalysts": "Agent additions; hotel contracting depth; ancillaries (forex, insurance); Middle East/Asia expansion.",
        "StagnationCatalysts": "AI direct-booking disintermediating agents; airline commission cuts; travel demand shocks.",
    },
    "TATACAP": {
        "AI_Moat": "Tata brand + funding cost + distribution = strong moat; AI underwriting table stakes. AI neutral.",
        "RevGrowthCeiling": "Multi-segment lending TAM huge; ceiling high.",
        "GrowthCatalysts": "AUM growth 20%+; branch expansion; wealth/insurance build.",
        "StagnationCatalysts": "Credit-cycle losses; RBI rules; bank competition.",
    },
    "TATATECH": {
        "AI_Moat": "Embedded ER&D with anchor OEM relationships (JLR/Tata) = moderate moat; GenAI automates routine engineering - pricing pressure unless it moves up value chain. AI threat + tool.",
        "RevGrowthCeiling": "Global ER&D services growing mid-teens; ceiling moderate-high.",
        "GrowthCatalysts": "EV program services; digital factory; aerospace vertical; anchor-client mining.",
        "StagnationCatalysts": "AI automating routine engineering work; client concentration; onshore cost.",
    },
    "TENNIND": {
        "AI_Moat": "Exhaust/clean-air OEM qualification = moderate moat, but EV transition structurally cuts exhaust content per vehicle. AI neutral.",
        "RevGrowthCeiling": "ICE content declining with EVs; aftermarket extends; ceiling low-moderate.",
        "GrowthCatalysts": "Aftermarket ride products; new SUV/ICE program content; exports.",
        "StagnationCatalysts": "EV transition; 2W/CV demand dips; steel cost.",
    },
    "THELEELA": {
        "AI_Moat": "Leela luxury brand + owned assets = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "Luxury occupancy x rate cycle; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; asset-light management contracts; F&B/events.",
        "StagnationCatalysts": "Travel shocks; capex/brand-standards cost; leverage.",
    },
    "TRAVELFOOD": {
        "AI_Moat": "Airport concession lock-ins (~26% lounge/QSR share) = location-monopoly moat, moderate-strong; AI neutral.",
        "RevGrowthCeiling": "Air-pax growth 10-15% + new airports; ceiling moderate-high.",
        "GrowthCatalysts": "Passenger traffic growth; new lounge/QSR concessions; airport retail.",
        "StagnationCatalysts": "Air-traffic shocks; concession rent escalation; brand competition.",
    },
    "TRUALT": {
        "AI_Moat": "Ethanol capacity (1,800 KLPD) + OMC offtake relationships = policy-dependent moderate moat; AI neutral.",
        "RevGrowthCeiling": "Ethanol blending targets (E20+) drive volumes; feedstock-capped; ceiling moderate-high.",
        "GrowthCatalysts": "Blending-mandate increases; grain-ethanol capacity; biofuel exports/SAF optionality.",
        "StagnationCatalysts": "Ethanol pricing disputes; molasses/grain cycles; policy shifts.",
    },
    "TVSSCS": {
        "AI_Moat": "Contract logistics network + TVS group credibility = moderate moat, thin margins; AI supply-chain planning a service upgrade. AI neutral-positive.",
        "RevGrowthCeiling": "India 3PL growing 15%+; ceiling moderate-high.",
        "GrowthCatalysts": "New verticals (defence, auto); warehouse network; digital supply-chain services.",
        "StagnationCatalysts": "Client insourcing; margin pressure; capital intensity.",
    },
    "UDS": {
        "AI_Moat": "IFM crew contracts thin-moderate moat; wage-inflation pass-through model; robotics/AI cleaning a long-term labour substitute. AI neutral.",
        "RevGrowthCeiling": "IFM market growing with commercial real estate; ceiling moderate.",
        "GrowthCatalysts": "Contract wins; client/sector diversification; bundled services.",
        "StagnationCatalysts": "Re-tender losses; wage inflation; client cost cuts.",
    },
    "TOLINS": {
        "AI_Moat": "Retread tread-rubber brand + network = thin-moderate moat; cheap new radial tyres erode retreading economics long-term. AI neutral.",
        "RevGrowthCeiling": "Retreading tied to CV fleet economics; ceiling low-moderate.",
        "GrowthCatalysts": "CV fleet growth; retread network expansion; tyre trading/distribution.",
        "StagnationCatalysts": "New-tyre price declines; radialisation; CV freight downturns.",
    },
    "TRANSRAILL": {
        "AI_Moat": "T&D EPC + tower manufacturing with qualification = moderate moat; grid capex golden cycle (incl AI data-centre load). AI neutral-positive.",
        "RevGrowthCeiling": "Transmission capex upcycle; ceiling moderate-high.",
        "GrowthCatalysts": "HV/EHV line awards; tower exports; substation packages.",
        "StagnationCatalysts": "Receivables; steel cost; KEC/Kalpataru competition.",
    },
    "TECHNOCRAF": {
        "AI_Moat": "Multi-domain public-infra EPC (water, roads, urban, power distribution) = moderate execution moat; AI neutral.",
        "RevGrowthCeiling": "Govt infra capex pipeline bound; ceiling moderate.",
        "GrowthCatalysts": "Water/wastewater awards; urban-infrastructure programs; power-distribution works.",
        "StagnationCatalysts": "Receivables; tender aggression; execution slippage.",
    },
    "TEMPSENS": {
        "AI_Moat": "Temperature-sensor/heater niche engineering with industrial qualifications = moderate moat; smart-sensor IIoT an upgrade path. AI neutral.",
        "RevGrowthCeiling": "Industrial sensing demand growing with process industries; ceiling moderate.",
        "GrowthCatalysts": "IIoT-enabled sensors; exports; new industrial verticals.",
        "StagnationCatalysts": "Import competition; industrial capex cycles; raw-material cost.",
    },
    "TURTLEMINT": {
        "AI_Moat": "Advisor-network insurance distribution platform (2-sided) = moderate moat; AI advice bots could bypass advisors - watch item; advisor relationships defend near-term. AI mixed.",
        "RevGrowthCeiling": "India insurance penetration rising; embedded distribution; ceiling high.",
        "GrowthCatalysts": "Advisor additions; insurer partnerships; motor/health policy growth.",
        "StagnationCatalysts": "AI direct-to-consumer underwriting/advice; commission regulation; advisor churn.",
    },
    "VIDYAWIRES": {
        "AI_Moat": "Winding wire/strips/busbar manufacturing with transformer qualifications = moderate moat; grid + AI data-centre electrical demand tailwind. AI neutral-positive.",
        "RevGrowthCeiling": "Transformer/electrical demand cycle; ceiling moderate.",
        "GrowthCatalysts": "Grid expansion demand; transformer OEM orders; capacity adds.",
        "StagnationCatalysts": "Copper cost; import competition; demand cyclicality.",
    },

    # ---------------- Batch U ----------------
    "UNIECOM": {
        "AI_Moat": "E-commerce ops SaaS stickiness (order/inventory workflows) = moderate moat; AI ops automation could leapfrog features - must keep shipping AI tooling. AI mixed.",
        "RevGrowthCeiling": "India e-com ops software growing with D2C wave; ceiling moderate-high.",
        "GrowthCatalysts": "Seller/D2C additions; omnichannel modules; international expansion.",
        "StagnationCatalysts": "Platform built-ins (Shopify/Flipkart); price competition; small-seller churn.",
    },
    "UNIMECH": {
        "AI_Moat": "Aerospace tooling/precision components with OEM & MRO qualifications = moderate-strong moat; AI neutral.",
        "RevGrowthCeiling": "Aero capex + India MRO growth; order-book bound; ceiling moderate-high.",
        "GrowthCatalysts": "MRO demand; export tooling; capacity additions.",
        "StagnationCatalysts": "Aero cycle downturns; approval timelines; competition.",
    },
    "URBANCO": {
        "AI_Moat": "Two-sided network (professionals x households) + service standardisation/trust = moderate-strong moat; AI matching/scheduling efficiency; gig-labour regulation the risk. AI positive tool.",
        "RevGrowthCeiling": "Home-services TAM large, organised shift early; ceiling high.",
        "GrowthCatalysts": "Category expansion (beauty, repairs); professional supply growth; new cities/countries; product attach.",
        "StagnationCatalysts": "Gig-labour regulation; professional churn; demand dips; local competition.",
    },
    "UTLSOLAR": {
        "AI_Moat": "Rooftop-solar brand + dealer channel = thin-moderate moat; AI neutral. PM Surya Ghar subsidy wave a demand tailwind.",
        "RevGrowthCeiling": "Rooftop solar installs accelerating with subsidies; ceiling moderate-high.",
        "GrowthCatalysts": "PM Surya Ghar volumes; inverter/panel brand share; dealer network depth.",
        "StagnationCatalysts": "Subsidy budget pauses; Chinese module pricing; dealer competition.",
    },
    "UTKARSHBNK": {
        "AI_Moat": "Rural/semi-urban microfinance + deposit franchise (Bihar/UP focus) = moderate moat; AI credit tools table stakes.",
        "RevGrowthCeiling": "Financial-inclusion credit pools large; ceiling high-ish.",
        "GrowthCatalysts": "Branch expansion; deposit growth; MFI book recovery.",
        "StagnationCatalysts": "MFI credit-cycle stress; regulation; competition.",
    },
    "USK": {
        "AI_Moat": "Karnataka roads/irrigation EPC execution = moderate regional moat; AI neutral.",
        "RevGrowthCeiling": "State govt capex cycle bound; ceiling moderate.",
        "GrowthCatalysts": "Irrigation/road awards; execution pace; order-book build.",
        "StagnationCatalysts": "State receivables; political cycle shifts; tender competition.",
    },

    # ---------------- Batch V ----------------
    "VALIANTLAB": {
        "AI_Moat": "Paracetamol API process scale = thin-moderate moat; commodity API price cycles dominate. AI neutral.",
        "RevGrowthCeiling": "Global paracetamol demand steady but price volatile; ceiling moderate-low.",
        "GrowthCatalysts": "Capacity adds; downstream integration; export registrations.",
        "StagnationCatalysts": "API price crashes; raw-material cost; Chinese competition.",
    },
    "VENTIVE": {
        "AI_Moat": "Luxury hotel/resort portfolio (India, Maldives, Sri Lanka) = asset moat; AI neutral.",
        "RevGrowthCeiling": "Luxury occupancy x rate cycle; ceiling moderate.",
        "GrowthCatalysts": "Room-rate upcycle; occupancy recovery; management contracts.",
        "StagnationCatalysts": "Travel shocks; leverage; Maldives geopolitical risk.",
    },
    "VIKRAN": {
        "AI_Moat": "Transmission/water/rail EPC execution = moderate moat; AI neutral.",
        "RevGrowthCeiling": "T&D + infra order flow; ceiling moderate.",
        "GrowthCatalysts": "T&D orders; water-infrastructure awards; rail projects.",
        "StagnationCatalysts": "Receivables; competition; execution slippage.",
    },
    "VIKRAMSOLR": {
        "AI_Moat": "Module manufacturing scale + ALMM protection + EPC = moderate moat; AI data-centre energy demand tailwind; pricing commodity-cyclical.",
        "RevGrowthCeiling": "India solar additions rising; ceiling high but cyclical.",
        "GrowthCatalysts": "Capacity expansion; export orders; NTPC/Adani-type EPC pipeline.",
        "StagnationCatalysts": "Chinese price wars; policy shifts; execution margins.",
    },
    "VMM": {
        "AI_Moat": "Value-retail hypermarket scale with ~80% private label = moderate-strong cost moat; AI inventory/planning a margin lever. AI neutral-positive.",
        "RevGrowthCeiling": "Tier-2/3 value retail growing 15%+; ceiling moderate-high.",
        "GrowthCatalysts": "Store additions; private-label depth; apparel/general-merchandise mix.",
        "StagnationCatalysts": "Value e-commerce/quick-commerce competition; fashion demand dips; store economics.",
    },
    "VSTL": {
        "AI_Moat": "ERW steel pipe manufacturing thin-moderate moat; AI neutral.",
        "RevGrowthCeiling": "Pipe demand cycle (water/infra/construction); ceiling moderate.",
        "GrowthCatalysts": "Capacity; infrastructure/water program orders; exports.",
        "StagnationCatalysts": "Steel cycles; import competition; margin thinness.",
    },
    "VMSTMT": {
        "AI_Moat": "Regional TMT-bar brand = thin-moderate moat; commodity steel economics. AI neutral.",
        "RevGrowthCeiling": "Construction demand cycle bound; ceiling moderate.",
        "GrowthCatalysts": "Capacity; construction/infrastructure demand; dealer depth.",
        "StagnationCatalysts": "Steel price cycles; sponge iron/scrap cost; regional competition.",
    },
    "VPRPL": {
        "AI_Moat": "Water-infrastructure EPC execution = moderate moat; AI neutral.",
        "RevGrowthCeiling": "Piped-water/irrigation program capex (JJM-type); ceiling moderate.",
        "GrowthCatalysts": "Water-supply awards; irrigation projects; O&M attach.",
        "StagnationCatalysts": "Receivables; tender competition; execution cost overruns.",
    },
    "VRAJ": {
        "AI_Moat": "Sponge iron → billets → TMT integration = thin-moderate commodity moat; AI neutral.",
        "RevGrowthCeiling": "Regional steel demand cycle; ceiling low-moderate.",
        "GrowthCatalysts": "Capacity; Chhattisgarh construction demand; integration margin.",
        "StagnationCatalysts": "Iron ore/coal cost; steel price cycles; power cost.",
    },

    # ---------------- Batch W ----------------
    "WAAREEENER": {
        "AI_Moat": "Multi-GW module scale + US export channel = moderate-strong moat among Indian peers; AI data-centre energy demand tailwind; pricing commodity-cyclical.",
        "RevGrowthCeiling": "India + US solar demand; ceiling high but cyclical.",
        "GrowthCatalysts": "US capacity/buildout; module GW expansion; green hydrogen optionality.",
        "StagnationCatalysts": "Chinese price wars; US tariff/IRA policy shifts; freight/logistics cost.",
    },
    "WAKEFIT": {
        "AI_Moat": "D2C brand + own mattress manufacturing = moderate cost moat; AI marketing tool; heavy competition. AI neutral.",
        "RevGrowthCeiling": "Sleep + home solutions growing 15-20%; ceiling moderate.",
        "GrowthCatalysts": "Furniture category expansion; offline stores; brand share gains.",
        "StagnationCatalysts": "Discount burn; Sleepwell/Kurlon incumbents; discretionary dips.",
    },
    "WCIL": {
        "AI_Moat": "Rail/multimodal freight with asset-light model = thin-moderate moat; rail policy dependence. AI neutral.",
        "RevGrowthCeiling": "Industrial freight volumes growing; ceiling moderate.",
        "GrowthCatalysts": "Rake capacity; multimodal terminals; industrial client wins.",
        "StagnationCatalysts": "Freight cycles; railway policy/pricing; large-client concentration.",
    },
    "WEWORK": {
        "AI_Moat": "WeWork India licence + enterprise flex demand + premium locations = moderate moat; hybrid-work tailwind. AI positive for flex demand.",
        "RevGrowthCeiling": "Flex workspace institutional demand growing; ceiling moderate-high.",
        "GrowthCatalysts": "Occupancy fill; location additions; enterprise pre-commits.",
        "StagnationCatalysts": "Global brand-licence fee burden; IT headcount freezes; competition.",
    },

    # ---------------- Batch X ----------------
    "XTRANET": {
        "AI_Moat": "Enterprise IT services moat thin; AI shifts value to GenAI-native delivery - pivot needed. AI threat + tool.",
        "RevGrowthCeiling": "India IT/digital spend growing; ceiling moderate.",
        "GrowthCatalysts": "Digital-transformation demand; managed services; client wallet share.",
        "StagnationCatalysts": "AI commoditising routine dev; competition; talent cost.",
    },

    # ---------------- Batch Y ----------------
    "YATHARTH": {
        "AI_Moat": "NCR/UP hospital brand + 2,800 beds = moderate-strong regional moat; AI operations a margin lever. AI positive.",
        "RevGrowthCeiling": "Regional healthcare demand structural; ceiling high-ish.",
        "GrowthCatalysts": "Bed additions/ARPOB growth; acquisitions; new hospital ramp.",
        "StagnationCatalysts": "Doctor cost inflation; capex drag; competition.",
    },
    "YATRA": {
        "AI_Moat": "Corporate-travel (TMC) relationships + fulfilment = moderate moat; AI self-booking by corporate clients a genuine threat; consolidation play. AI mixed.",
        "RevGrowthCeiling": "India corporate travel growing with GDP; ceiling moderate.",
        "GrowthCatalysts": "Corporate client wins; SME segment; hotel packages.",
        "StagnationCatalysts": "AI self-serve booking; client concentration; fee compression.",
    },

    # ---------------- Batch Z ----------------
    "ZAGGLE": {
        "AI_Moat": "Corporate spend-management platform with bank partnerships + tax/ERP integrations = moderate moat; AI expense automation both threat and feature. AI mixed-positive.",
        "RevGrowthCeiling": "India corporate card/spend market growing; ceiling moderate-high.",
        "GrowthCatalysts": "Corporate client adds; card spend volumes; new products (tax, payroll).",
        "StagnationCatalysts": "Fintech/bank competition (EnKash, Karbon); PPI regulation; client concentration.",
    },
}


def main():
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    for col in NEW_COLS:
        if col not in fieldnames:
            fieldnames.append(col)
    missing = [t for t in NOTES if t not in {r["Ticker"] for r in rows}]
    assert not missing, f"unknown tickers: {missing}"

    patched = 0
    for row in rows:
        note = NOTES.get(row["Ticker"])
        if not note:
            continue
        for col in NEW_COLS:
            if note.get(col):
                row[col] = note[col]
        patched += 1

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"patched {patched}/{len(NOTES)} tickers, {len(rows)} rows total")
    subprocess.run(["python3", str(ROOT / "make_docs.py")], check=True)


if __name__ == "__main__":
    main()
