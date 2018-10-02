# coding: utf8
from __future__ import unicode_literals


VERBS = set("""
 abaisser abandonner abdiquer abecquer aberrer abhorrer abjurer ablater
 abluer ablutionner abominer abonder abonner aborder aborner aboucher abouler
 abraquer abraser abreuver abricoter abriter absenter absinther absorber abuser
 abéliser abîmer académiser acagnarder accabler accagner accaparer accastiller
 accentuer accepter accessoiriser accidenter acclamer acclimater accointer
 accolader accoler accommoder accompagner accorder accorer accoster accoter
 accouder accouer accoupler accoutrer accoutumer accouver accrassiner accrocher
 accréditer acculer acculturer accumuler accuser acenser achalander acharner
 achopper achromatiser aciduler aciériser acliquer acoquiner acquitter acquêter
 actiniser actionner activer actualiser acupuncturer acyler acétaliser acétyler
 additionner adenter adieuser adirer adjectiver adjectiviser adjurer adjuver
 admirer admonester adoniser adonner adopter adorer adorner adosser adouber
 adsorber aduler adverbialiser affabuler affacturer affairer affaisser affaiter
 affamer affecter affectionner affermer afficher affider affiler affiner
 affirmer affistoler affixer affleurer afflouer affluer affoler afforester
 affouiller affourcher affriander affricher affrioler affriquer affriter
 affruiter affubler affurer affûter afistoler africaniser agatiser agenouiller
 aggraver agioter agiter agoniser agourmander agrafer agrainer agresser
 agriffer agripper agrouper agrémenter aguetter aguicher ahaner aheurter aicher
 aigretter aiguer aiguiller aiguillonner aiguiser ailer ailler ailloliser
 aimer airer ajointer ajourer ajourner ajouter ajuster ajuter alambiquer
 alarmer alcaliniser alcaliser alcooliser alcoolyser alcoyler aldoliser alerter
 aleviner algorithmiser algébriser algérianiser aligner alimenter alinéater
 aliter alkyler allaiter allectomiser allitiser allivrer allocutionner alloter
 alluder allumer allusionner alluvionner allyler allégoriser aloter alpaguer
 alphabétiser alterner aluminer aluminiser aluner alvéoler alvéoliser
 amadouer amalgamer amariner amarrer amateloter ambitionner ambler ambrer
 amender amenuiser ameulonner ameuter amiauler amicoter amidonner amignarder
 amignoter amignotter aminer ammoniaquer ammoniser ammoxyder amocher amouiller
 amourer amphotériser ampouler amputer amunitionner amurer amuser améliorer
 anagrammatiser anagrammer analyser anamorphoser anaphylactiser anarchiser
 anathématiser anatomiser ancher anchoiter ancrer anecdotiser anglaiser angler
 angoisser anguler angéliser animaliser animer aniser ankyloser annexer
 annoter annualiser annuler anodiser anser antagoniser anthropomorphiser
 anticoaguler antidater antiparasiter antiquer antiseptiser antéposer
 anuiter aoûter apaiser apetisser apeurer apiquer aplaner apologiser
 aponter aponévrotomiser aposter apostiller apostropher apostumer apothéoser
 appareiller apparenter appeauter appertiser appliquer appointer appoltronner
 apporter apposer apprivoiser approcher approuver approvisionner approximer
 apprêter apurer apériter aquareller arabiser aramer araméiser araser arbitrer
 arboriser archaïser architecturer archiver ardoiser arer argenter argoter
 argumenter arianiser arimer ariser aristocratiser aristotéliser arithmétiser
 armaturer armer arnaquer aromatiser arpenter arquebuser arquer arracher
 arrenter arrher arrimer arriser arriver arroser arrêter arsouiller articler
 artificialiser artistiquer artérialiser aryler arçonner aréniser ascensionner
 aseptiser asexuer asiatiser aspecter asphalter aspirer assabler assaisonner
 assassiner assembler assener assermenter asserter assibiler assigner assimiler
 assoiffer assoler assommer assoner assoter assumer assurer asséner asticoter
 athéiser atlantiser atomiser atourner atropiniser attabler attacher attaquer
 attenter attentionner atterrer attester attifer attirer attiser attitrer
 attraper attremper attribuer attrister attrouper atténuer aubiner
 auditer auditionner augmenter augurer aulofer auloffer aumôner auner auréoler
 authentiquer autoaccuser autoadapter autoadministrer autoagglutiner
 autoallumer autoamputer autoanalyser autoancrer autoassembler autoassurer
 autocastrer autocensurer autocentrer autociter autoclaver autocoller
 autocondenser autocongratuler autoconserver autoconsommer autocontester
 autocratiser autocritiquer autodicter autodiscipliner autodupliquer
 autodénigrer autodésigner autodéterminer autoenchâsser autoenseigner
 autofertiliser autoformer autofretter autoféconder autogouverner autogreffer
 autolimiter autolyser automatiser automitrailler automutiler automédiquer
 autopersuader autopiloter autopolliniser autoporter autopositionner
 autopropulser autorelaxer autoriser autoréaliser autoréguler autoréparer
 autostimuler autostopper autosubsister autosuggestionner autotomiser
 autovacciner autoventiler autoéduquer autoépurer autoéquiper autoévoluer
 avaler avaliser aventurer aveugler avillonner aviner avironner aviser
 aviver avoiner avoisiner avorter avouer axer axiomatiser azimuter azoter
 aéroporter aérosonder aérotransporter babiller babouiner bachonner bachoter
 badauder badigeonner badiner baffer bafouer bafouiller bagarrer bagoter
 bagouler baguenauder baguer baguetter bahuter baigner bailler baiser baisoter
 baisouiller baisser bakéliser balader baladiner balafrer balancetiquer
 baleiner baliser baliver baliverner balkaniser ballaster baller ballonner
 balourder balustrer bambocher banaliser bancariser bancher bander banderiller
 bandonéoner banner banquer baptiser baragouiner barander baraquer baratiner
 barauder barbariser barber barbeyer barboter barbouiller barder barguigner
 baroniser baronner baroquiser barouder barreauder barrer barricader barroter
 barytonner basaner basculer baser bassiner baster bastillonner bastinguer
 bastonner bastringuer batailler batifoder batifoler batiker batiller batourner
 baudouiner bauxitiser bavacher bavarder baver bavocher bavoter bayer bazarder
 becter bedonner beigner beloter belotter belouser benzoyler benzyler berdiner
 berlurer berner bertauder bertillonner bertouder besogner bestialiser beugler
 biaiser bibarder bibeloter biberonner bicarbonater bicher bichonner
 bidistiller bidonner bidonvilliser bidouiller biduler biffer biffetonner
 biftonner bifurquer bigarrer bigler bigophoner bigorner bijouter biler
 billarder billebarrer billebauder biller billonner biloquer biner binoter
 biotraiter biotransformer biper bipolariser biscoter biscuiter biseauter
 biser bisiallitiser bismuther bisouter bisquer bissecter bisser bistourner
 bistrouiller biter bitter bitturer bitumer bituminer bituminiser biturer
 bivouaquer bizouter bizuter blablater blackbouler blaguer blaireauter blairer
 blaser blasonner blesser bleuter blinder blinquer bloquer blouser bluetter
 bluter bobiner bocarder boetter boffumer boguer boiser boissonner boitailler
 boitiller boitter bolcheviser bolchéviser bolincher bombarder bomber bombiller
 bonder bondieuser bondonner bondériser bonimenter boquillonner borater
 border bordurer bordéliser boriquer borner borosilicater borurer boscarder
 bosseyer bossuer bostonner botaniser botter bottiner boubouler boucaner
 boucher bouchonner boucler bouder boudiner bouffarder bouffer bouffonner
 bougonner bouiller bouillonner bouillotter bouler boulevarder bouleverser
 boulocher boulonner boulotter boultiner boumer bouquer bouquiner bourder
 bourgeonner bourlinguer bourraquer bourrer bourriquer bourser boursicoter
 boursouffler boursoufler bousculer bouser bousiller boustifailler boutader
 boutiquer boutonner bouturer bouziller bovaryser bowaliser boxer boyauter
 boësser braconner brader brailler braiser braisiller bramer brancarder
 brandiller brandonner brandouiller branler branlocher braquer braser brasiller
 brasseyer bravader braver bredouiller brelander breller bretailler bretauder
 bretter brichetonner bricoler brider briefer brifer brifetonner briffer
 briffetonner brifter briftonner brigander briguer brillanter brillantiner
 brimbaler brimballer brimer brinder bringuebaler bringueballer bringuer
 brinqueballer briocher brioler briquer briser britanniser brocanter brocarder
 broder bromer bromurer broncher bronzer brosser brouetter brouillarder
 brouillonner broussailler brousser brouter bruiner bruisser bruiter brumer
 bruncher brusquer brutaliser bruter brésiller brétailler brêler brûler
 bucoliser budgétiser buer buffler buffériser bugler bugner buiser buissonner
 buquer bureaucratiser buriner buser busquer buter butiner butonner butter
 buvoter byzantiner bâcher bâcler bâfrer bâiller bâillonner bâtarder bâtonner
 bécotter béliner bémoliser béquiller bétonner bêcher bêler bêtiser bûcher
 cabaler cabaner cabosser caboter cabotiner cabrer cabrioler cacaber cacaoter
 cacher cachetonner cachotter cadastrer cadavériser cadeauter cadetter cadoter
 cadrer cafarder cafeter cafouiller cafter cageoler cagnarder cagner caguer
 caillebotter cailler caillouter cajoler calaminer calamistrer calamiter
 calandrer calaouer calciner calculer calencher caler calfater calfeutrer
 caller calmer caloriser calotter calquer calter camarder cambrer cambrioler
 cameloter camer camionner camisoler camoufler camper camphrer canadianiser
 canarder cancaner canceller cancériser candidater caner canneller canner
 cannibaliser canoniser canonner canoter canter cantiner cantonnaliser
 canuler caoutchouter caparaçonner caper capeyer capillariser capitaliser
 capituler caponner caporaliser capoter capser capsuler capter captiver
 capuchonner caquer carabiner caracoler caracouler caractériser caramboler
 caraméliser carapater carbonater carboner carboniser carbonitrurer carbonyler
 carburer carcailler carder cardinaliser carer caresser carguer caricaturer
 carminer carniser carotter caroubler carrer carrioler carrosser cartelliser
 cartonner cascader casemater caser caserner casquer castagner castiller
 cataboliser cataloguer catalyser catapulter cataracter catastropher catcher
 cathétériser catiner catéchiser catégoriser cauchemarder causaliser causer
 cautériser cavalcader cavaler caver caviarder ceintrer ceinturer cendrer
 centraliser centrer centupler cercler cerner cesser chabler chabroler
 chahuter chalouper chaluter chamailler chamarrer chambarder chambouler
 chambrer chamoiser champagniser champignonner champouigner champouiner
 chanfrer chanlatter chansonner chanter chantonner chantourner chaparder
 chaperonner chapitrer chaponner chapoter chaptaliser charançonner charbonner
 chardonner chariboter charioter charivariser charlataner charmer charogner
 charquer charronner charruer charteriser chatertonner chatonner chatouiller
 chauber chaucher chauder chauffer chauler chaumer chausser chavirer chaîner
 cheminer chemiser chenailler chenaler chercher cherrer chevaler chevaucher
 chevretter chevronner chevroter chiader chialer chicaner chicorer chicoter
 chiffonner chiffrer chigner chimiquer chimiser chimisorber chiner chinoiser
 chipoter chiquenauder chiquer chirurgicaliser chlinguer chlorater chlorer
 chloroformer chloroformiser chlorométhyler chlorurer chocolater choper
 chopper choquer choser chouanner chouchouter chougner chouler chouraver
 chouriner christianiser chromaluminiser chromater chromatiser chromer
 chroniciser chroniquer chrysalider chuchoter chuinter chuter châtaigner
 chènevotter chélater chénevotter chêmer chômer cibler cicatriser cicéroniser
 ciller cimenter cingler cintrer cinématiser circonvoisiner circuiter
 circuler cirer cisailler citer citronner civiliser clabauder claboter clairer
 clamer clamper clampiner clampser clamser claper clapoter clapper clapser
 claquer claquetter claudiquer claustrer claveliser claver clavetter clayonner
 cligner clignoter climatiser clinquanter clinquer cliper cliquer clisser
 clochardiser clocher clocter cloisonner cloner cloper clopiner cloquer clouer
 cloîtrer cléricaliser clôturer coaccuser coacerver coacher coadapter
 coagglutiner coaguler coaliser coaltarer coaltariser coanimer coarticuler
 cocarder cocaïniser cocheniller cocher cochonner coconner cocooner cocoter
 coder codiller coexister coexploiter coexprimer coffiner coffrer cofonder
 cogner cohabiter cohober cohériter coiffer coincher colchiciner collaber
 collationner collecter collectionner collectiviser coller collisionner
 colluvionner colmater colombiner coloniser colorer coloriser colostomiser
 colporter colpotomiser coltiner columniser combiner combler commander
 commenter commercialiser comminer commissionner commotionner commuer
 communautariser communiquer communiser commuter commémorer compacter comparer
 compenser compiler compisser complanter complexer complimenter compliquer
 complémenter complétiviser comporter composer composter compoter compounder
 comprimer comptabiliser compter compulser computer computériser concentrer
 concerner concerter concher conciliabuler concocter concorder concrétionner
 concubiner condamner condenser condimenter conditionner confabuler
 confesser confessionnaliser configurer confiner confirmer confisquer confiter
 conformer conforter confronter confusionner congestionner conglober
 congoliser congratuler coniser conjecturer conjointer conjuguer conjurer
 conniver connoter conquêter consacrer conscientiser conseiller conserver
 consister consoler consolider consommariser consommer consonantiser consoner
 conspirer conspuer constater consteller conster consterner constiper
 constitutionnaliser consulter consumer contacter contagionner containeriser
 contaminer contemner contempler conteneuriser contenter conter contester
 contingenter continuer contorsionner contourner contracter contractualiser
 contraposer contraster contrebouter contrebuter contrecalquer contrecarrer
 contreficher contrefraser contremander contremanifester contremarcher
 contreminer contremurer contrenquêter contreplaquer contrepointer contrer
 contrespionner contretyper contreventer contribuer contrister controuver
 contrôler contusionner conventionnaliser conventionner conventualiser
 convoiter convoler convoquer convulser convulsionner cooccuper coopter
 coorganiser coparrainer coparticiper copermuter copiner copolycondenser
 coprésenter coprésider copser copter copuler copyrighter coqueliner
 coquer coqueriquer coquiller corailler corder cordonner cornaquer cornemuser
 corporiser correctionaliser correctionnaliser correler corroborer corroder
 corser corticaliser coréaliser coréguler cosigner cosmétiquer cosser costumer
 cotillonner cotiser cotonner cotransfecter couaquer couarder couchailler
 couchoter couchotter coucouer coucouler couder coudrer couillonner couiner
 coulisser coupailler coupeller couper couperoser coupler couponner courailler
 courber courbetter courcailler couronner courser court-circuiter courtauder
 cousiner coussiner couturer couver coéditer coéduquer coïncider coïter coûter
 cracher crachiner crachoter crachouiller crailler cramer craminer cramper
 crampser cramser craner cranter crapahuter crapaüter crapser crapuler
 craquer crasher craticuler cratoniser cratériser cravacher cravater crawler
 creuser criailler cribler criminaliser criquer crisper crisser cristalliser
 critiquer crocher croiser croquer croskiller crosser crotoniser crotter
 croupionner crouponner croustiller croûter croûtonner cryoappliquer
 cryocoaguler cryoconcentrer cryodécaper cryofixer cryogéniser cryomarquer
 cryosorber cryoébarber crypter crâner crânoter crédibiliser créditer
 créoliser créosoter crépiner crépiter crésyler crétiniser crêper crêter crôler
 cueiller cuider cuisiner cuiter cuivrer culbuter culer culminer culotter
 cultiver cumuler curariser curedenter curer curetter cuter cutiniser cuver
 cyaniser cyanoser cyanurer cybernétiser cycler cycliser cycloner cylindrer
 câbler câliner cémenter céphaliser céramiser césariser côcher dactylocoder
 daguerréotyper daigner dailler daller damasquiner damer damner damouritiser
 danser dansoter dansotter darder dater dauber daufer dauffer daupher daïer
 demander demeurer dentaliser denter desceller designer despotiser desquamer
 dessaigner dessaisonaliser dessaisonner dessaler dessaliniser dessangler
 desseller desserrer dessiller dessiner dessoler dessoucher dessouder dessouler
 dessuinter destiner destituer deviner deviser dextriniser diaboliser
 diagnostiquer diagonaliser dialectaliser dialectiser dialoguer dialyser
 diapasonner diaphaniser diaphanéiser diaphragmer diaprer diastaser diazoter
 dichotomiser dicter diffamer diffluer difformer diffracter diffuser difluorer
 digresser dihydroxyler diioder dilapider dilater diligenter diluer
 diminuer dimériser dindonner dinguer dinitrer diogéniser diphtonguer diplexer
 diplômer dirimer discerner discipliner disconnecter discontinuer discorder
 discriminer discréditer discrétiser disculper discutailler discuter disjoncter
 dismuter dispatcher dispenser disperser disponibiliser disposer
 disputailler disputer disquer dissembler disserter dissimiler dissimuler
 dissoner dissuader disséminer distiller distinguer distribuer disubstituer
 divaguer diverticuler diviniser diviser divulguer diéséliser dociliser
 documenter dodeliner dodiner dogmatiser doguer doigter dolenter doler
 domanialiser domestiquer dominer dompter donjuaniser donner doper dorer
 dormailler dormichonner dorsaliser doser dosser doter douaner doublecliquer
 doublonner doucher douer douiller douter dracher drageonner dragonner draguer
 dramatiser draper draver dresser dribbler driller driver droguer droitiser
 dropper drosser dualiser dudgeonner duiter dumper duper duplexer duplicater
 duraminiser durer dynamiser dynamiter dysfonctionner déactiver déafférenter
 déankyloser débagouler débaguer débaleiner débaliser déballaster déballer
 débalourder débanaliser débander débanquer débaptiser débarbouiller débarder
 débarquer débarrer débarricader débaucher débecquer débecqueter débecter
 débenzoler débenzoyler débeurrer débieller débiffer débiliser débiliter
 débiller débiner débiter débitumer débituminer déblinder débloquer débobiner
 déboguer déboiser débonder débondonner déborder débosser débotter déboucher
 débouder débouler déboulonner débouquer débourber débourgeoiser débourrer
 déboussoler débouter déboutonner déboîter débraguetter débrailler débraiser
 débraser débrider débriefer débringuer débrocher débromer débronzer
 débroussailler débrousser débruter débucher débudgétiser débuller
 débusquer débutaniser débuter débutter débâcher débâcler débâillonner
 débétonner débêcher débûcher décabosser décadrer décaféiner décaféiniser
 décaisser décalaminer décalcariser décaler décalfater décalotter décalquer
 décamper décanadianiser décanailler décaniller décanner décanter décantonner
 décaoutchouter décaper décapitaliser décapiter décapitonner décapoter
 décapuchonner décarbonater décarboniser décarbonyler décarboxyler décarburer
 décarotter décarrer décartelliser décartonner décarêmer décaser décaserner
 décatholiciser décatégoriser décauser décavaillonner décaver décentraliser
 décercler décerner décesser déchagriner déchaler déchanter déchaper
 déchaptaliser décharançonner décharner déchatonner déchauler déchaumer
 déchaîner décheviller déchevêtrer déchiffonner déchiffrer déchirer déchlorer
 déchoquer déchristianiser déchromer décibler décider déciller décimaliser
 décintrer décirer déciviliser déclamer déclarer déclencher déclimater décliner
 décliquer décliver déclocher décloisonner déclouer décloîtrer décléricaliser
 décoaguler décocaïniser décocher décoconner décoder décoeurer décoffrer
 décollectiviser décoller décolmater décoloniser décolorer décombrer
 décommuniser décompacter décompartimenter décompenser décomplexer décompliquer
 décompresser décomprimer décompter déconcentrer déconcerter décondamner
 déconfessionnaliser déconforter décongestionner déconnecter déconner
 déconsacrer déconseiller déconsigner déconsolider déconstiper
 décontaminer décontextualiser décontracter décontracturer décontrôler
 décoquer décoquiller décorder décorer décorner décortiquer décoter décotter
 découenner découler découper découpler décourber découronner décraber
 décranter décrapouiller décravater décreuser décriminaliser décriquer
 décristalliser décrocher décroiser décrotter décroûter décruer décruser
 décrédibiliser décréditer décrémenter décrépiter décrétiniser décrêper
 décuivrer déculotter déculpabiliser déculturer décupler décurariser décuscuter
 décycliser décérébeller dédaigner dédaller dédamer dédiviniser dédoler
 dédorer dédosser dédotaliser dédouaner dédoubler dédramatiser défacturer
 défaner défarder défarguer défasciser défatiguer défaufiler défauner défausser
 défaçonner défenestrer déferler déferrailler déferrer déferriser défertiliser
 défeutrer défibrer défibriller défibriner déficher défidéliser défigurer
 défilialiser défilocher défiscaliser déflagrer déflaquer déflater déflegmer
 déflorer défluer défluorer défocaliser défolioter défonctionnariser déforester
 déformater déformer défouetter défouler défourailler défourner défourrer
 défranchiser défranciser défrapper défretter défricher défrimer défringuer
 défriser défrisotter défroisser défroquer défruiter défubler défumer défuncter
 défâcher déféminiser dégainer dégalonner déganter dégarer dégarouler
 dégasconner dégasoliner dégauchiser dégausser dégazer dégazoliner dégazonner
 dégermer dégingander dégivrer déglaiser déglaçonner déglinguer déglobuliser
 déglutiner déglycériner dégobiller dégoiser dégommer dégonder dégonfler
 dégotter dégoudronner dégouliner dégoupiller dégoutter dégoûter dégrabatiser
 dégrafer dégrainer dégraisser dégrammaticaliser dégranuler dégraphiter
 dégravillonner dégrener dégriffer dégriller dégringoler dégripper dégriser
 dégrouiller dégrouper dégréciser dégréner dégueniller dégueuler déguiser
 déguster dégêner dégîter déhaler déhancher déharder déharnacher déhelléniser
 déhotter déhouiller déhourder déhousser déhâler déidéologiser déioniser
 déjanter déjeuner déjointer déjouer déjouter déjucher déjudaïser délabialiser
 délabyrinther délactoser délainer délaisser délaiter délaminer délarder
 délaver délecter délenter délester déleucocyter délicoter déligner déligoter
 délimoner délinquer délinéamenter délinéariser délirer délisser délister
 délivrer délocaliser déloquer délourder délover délurer délustrer déluter
 délégitimer démacadamiser démacler démagnétiser démailler démaillonner
 démancher démandriner démaniller démanoquer démantibuler démaoïser démaquer
 démarcher démargariner démarginer démarquer démarrer démarxiser démascler
 démasquer démasselotter démastiquer démathématiser dématriculer dématérialiser
 démaçonner démembrer démensualiser démerder démesurer démeubler démieller
 déminer déminéraliser démissionner démobiliser démocratiser démoder démoduler
 démonter démontrer démonétiser démoraliser démorphiner démorphiniser démotiver
 démouler démoustiquer démucilaginer démultiplexer démurer démutiser
 démysticiser démyéliniser démécaniser démédicaliser démériter démétalliser
 déméthyler démêler dénasaliser dénationaliser dénatter dénaturaliser dénaturer
 déniaiser dénicher dénicotiniser dénigrer dénitrater dénitrer dénoder
 dénominer dénommer dénoter dénouer dénoyauter dénucléariser dénuder dénuer
 dénébuliser déodorer déodoriser dépaganiser dépageoter dépaginer dépagnoter
 dépailler dépajoter dépalataliser dépaler dépalettiser dépalissader dépalisser
 dépanner dépanouiller dépapiller dépapilloter déparaffiner déparasiter
 déparcher dépareiller déparementer déparer déparfumer déparisianiser déparler
 départementaliser dépassionner dépassiver dépastiller dépatouiller dépatter
 dépayser dépeigner dépeinturer dépeinturlurer dépelliculer dépelotonner
 dépenser dépentaniser dépersonnaliser dépersuader dépeupler déphaser
 déphlogistiquer déphonologiser déphosphater déphosphorer dépiauter dépierrer
 dépigeonniser dépigmenter dépiler dépingler dépiquer dépister dépiter
 déplafonner déplanquer déplanter déplaquetter déplatiner déplisser déplomber
 déplumer déplâtrer dépocher dépoiler dépointer dépoitrailler dépolariser
 dépolluer dépolymériser dépontiller dépopulariser déporter déposer déposter
 dépoudrer dépouiller dépoétiser dépraver dépresser dépressuriser déprimer
 dépriver déprogrammer déprolétariser dépropaniser déprovincialiser dépréparer
 dépulper dépunaiser dépurer députer dépécorer dépénaliser dépêcher dépêtrer
 déqueusoter déquiller déraber déraciner dérader dérailler déraisonner
 déramer déraper déraser dérater dérationaliser dératiser dérembourser
 dérestaurer dérider dériver dérober dérocher dérocter déroder déroquer
 dérouler dérouter dérueller déruraliser dérâper déréaliser dérégionaliser
 déréguler déréprimer désabonner désabouter désabriter désabuser désaccentuer
 désaccorder désaccorer désaccoupler désaccoutumer désachalander désacraliser
 désadapter désadopter désaffecter désaffectionner désaffleurer désaffourcher
 désaffubler désafférenter désagater désagrafer désailer désaimanter désaimer
 désaisonnaliser désaisonner désajuster désalcoyler désaligner désaliniser
 désallouer désalper désalphabétiser désaluminiser désamarrer désambiguer
 désamianter désamidonner désaminer désaméricaniser désancrer désangler
 désangoisser désannexer désapeurer désappareiller désapparenter désappointer
 désapprovisionner désarabiser désarchiver désargenter désaristocratiser
 désaromatiser désarrimer désarticuler désarçonner désasphalter désaspirer
 désassembler désassibiler désassimiler désassurer désatelliser désatomiser
 désattrister désaturer désauber désaveugler désavouer désaxer désazoter
 déschister déschlammer déscolariser désectoriser désemballer désembarquer
 désembaucher désembobiner désembourber désembourgeoiser désembouteiller
 désembringuer désembrocher désembrouiller désembroussailler désembuer
 désemmancher désemmieller désemmitoufler désemmurer désemmêler désempailler
 désemparer désemphatiser désempierrer désempiler désemplumer désempoisonner
 désempoissonner désemprisonner désemprunter désempêtrer désenamourer
 désencanailler désencapsuler désencapuchonner désencarter désencartonner
 désencastrer désencaustiquer désenchanter désenchaîner désenchevêtrer
 désenclaver désenclencher désenclouer désencoller désencombrer désencorder
 désencroûter désencuivrer désendetter désendimancher désenfiler désenflammer
 désenfourner désenfumer désengazonner désenglober désengluer désengommer
 désenivrer désenliser désenrhumer désenrober désenrouer désenrubanner
 désenrôler désensabler désensacher désenseigner désenserrer désensibiliser
 désensommeiller désensoufrer désentartrer désenterrer désenthousiasmer
 désentoiler désentortiller désentraver désenturbanner désentêter désenvaser
 désenvenimer désenverguer désenvoûter désergoter déserter désertiser
 désexciter désexualiser déshabiliter déshabiller déshabiter déshabituer
 désharnacher désharponner désherber désheurer déshomogénéiser déshonorer
 déshuiler déshumaniser déshydrater déshémoglobiniser déshériter désiconiser
 désidéologiser désigner désiler désilicater désillusionner désillustrer
 désimbriquer désimmuniser désimperméabiliser désincarner désincorporer
 désinculper désindemniser désindexer désindividualiser désindustrialiser
 désinfatuer désinfecter désinformatiser désinformer désinféoder désinhiber
 désinsectiser désinstaller désintellectualiser désintoxiquer désintriquer
 désinvaginer désinviter désioniser désirer désislamiser désisoler désister
 désobstruer désobuser désoccidentaliser désocculter désoccuper désocialiser
 désoeuvrer désofficialiser désoler désolidariser désolvater désongler
 désophistiquer désopiler désorber désorbiter désordonner désorganiser
 désorienter désosser désoufrer désoutiller désoxyder déspiraliser
 désponsoriser déspécialiser déstabiliser déstaliniser déstandardiser
 déstocker déstresser déstructurer désubjectiviser désubventionner désucrer
 désulfater désulfiter désulfurer désurbaniser désurchauffer désurtaxer
 désynchroniser désyndicaliser désécailler déséchafauder déséchouer déséclairer
 déségrégationner désélectriser désémantiser désémulsionner désénamourer
 désépargner désépauler désépingler déséquetter déséquilibrer déséquiper
 désétamer désétatiser déséthaniser désétoffer détabler détabouiser détacher
 détaler détalinguer détaller détalonner détalquer détamiser détanner
 détaper détapisser détartrer détatouer détaxer détayloriser détechnocratiser
 déterminer déterminiser déterrer détester déthéiner déthésauriser
 détimbrer détiquer détirefonner détirer détisser détitrer détoner détonner
 détotaliser détourer détourner détoxiquer détracter détrancaner détrancher
 détrapper détraquer détremper détresser détribaliser détricoter détripler
 détromper détroncher détronquer détroquer détrousser détrôner détuber
 dévaginer dévaler dévaliser dévaloriser dévaluer dévaser dévaster développer
 déventer dévergonder déverguer déverrouiller déverser dévider dévirer
 dévirginiser déviriliser déviroler dévisser dévitaliser dévitaminer
 dévocaliser dévoiler dévoiser dévoler dévolter dévorer dévouer dévriller
 dézinguer déélectroner dîmer dîner ecchymoser ectomiser eczématiser effaner
 effaroucher effectuer effeuiller effiler effilocher effiloquer efflanquer
 efflorer effluer effluver effondrer effriter effruiter effumer effuser
 ellipser embabouiner emballer emballotter embaluchonner embalustrer embander
 embarbouiller embarder embarquer embarrer embastiller embastionner embaucher
 embecquer emberlicoquer emberlificoter emberloquer emberlucoquer embesogner
 embidonner embieller emblaver embler embobeliner embobiner emboiser emboliser
 embosser emboucaner emboucauter emboucher emboucler embouer embouquer
 embourgeoiser embourrer embourser embouser embouteiller embouter emboîter
 embraquer embraser embrelicoquer embreuver embrigader embringuer embrocher
 embrouiller embroussailler embruiner embrumer embuer embusquer embâtonner
 embêter embûcher emmagasiner emmailler emmailloter emmancher emmarquiser
 emmenotter emmerder emmeuler emmiasmer emmieller emmitonner emmitoufler
 emmotter emmoufler emmouscailler emmurailler emmurer emmêler empaffer
 empaler empalmer empanacher empanner empapaouter empapilloter emparadiser
 emparquer empatter empaumer empeigner empeloter empelotonner empenner
 emperler emperruquer empester emphatiser empierrer empiffrer empiler empirer
 emplanter emplastrer emplomber emplumer emplâtrer empocher empoicrer empoigner
 empointer empoisonner empoisser empoissonner empommer emporter empoter
 empourprer empouter empresser emprisonner emprunter emprésurer empêcher
 empêtrer enamourer enarbrer encabaner encadrer encagouler encaisser encalminer
 encanailler encaper encapsuler encapuchonner encaquer encarter encartonner
 encaserner encaster encastrer encaustiquer encaver enceinter enceintrer
 encenser encercler enchanter enchaper enchaperonner encharbonner encharner
 enchausser enchaussumer enchaîner enchemiser enchevaler enchevaucher
 enchevêtrer enchâsser encirer enclaver enclencher enclouer encloîtrer encocher
 encoder encoffrer encoigner encoller encombrer encorbeller encorder encorner
 encoubler encourtiner encrer encrister encroiser encrotter encrouer encroûter
 encuivrer enculer encuver encéphaliser endauber endenter endetter endeuiller
 endiamanter endiguer endimancher endisquer endivisionner endoctriner
 endosmoser endosser endothélialiser endouzainer endrailler endurer endêver
 enfariner enfaçonner enfaîter enfermer enferrer enficher enfieller enfiler
 enflaquer enfler enfleurer enformer enfosser enfourcher enfourner enfricher
 enfutailler enfûter engainer engaller engamer enganter engargousser engaver
 engeigner engendrer engerber englaçonner englober engluer engober engommer
 engouffrer engouler engraisser engraver engrisailler engrosser engrêler
 engueuler engueuser enguicher enguirlander enharnacher enherber enivrer
 enjaler enjamber enjanter enjoliver enjouer enjouguer enjuguer enjuiver
 enjôler enkikiner enkyster enlarmer enligner enlinceuler enliser enluminer
 enquiller enquinauder enquiquiner enquêter enraciner enrailler enregistrer
 enrober enrocher enrouer enrouiller enrouler enrubanner enrégimenter enrésiner
 enrôler ensabler ensaboter ensacher ensafraner ensaisiner ensanglanter
 ensauver enseigner enseller enserrer enseuiller ensiler ensiloter ensimer
 ensommeiller ensoufrer ensouiller ensoupler ensoutaner ensucrer ensuifer
 ensuquer entabler entacher entailler entamer entaquer entartrer enter enterrer
 enticher entoiler entomber entonner entortiller entourer entourlouper
 entraccorder entraccuser entradmirer entraider entraver entraîner entrebâiller
 entrecouper entrecroiser entredonner entredévorer entrefermer entregreffer
 entrelarder entrelouer entremêler entrepardonner entrepointiller entreposer
 entrequereller entrer entreregarder entreserrer entretailler entreteiller
 entretuer entrevoûter entrexaminer entuber enturbanner entériner entêter
 envacuoler envaler envaper envaser envelopper envenimer enverguer enverrer
 envirer environner envoiler envoisiner envoler envoûter enwagonner ergoter
 esbigner esbroufer esbrouffer escadronner escalader escaler escaloper
 escamper escaper escarbiller escarbouiller escarmoucher escarper escher
 esclaffer escobarder escompter escorter escrimer escroquer esgourder esmiller
 espagnoliser espalmer espionner espoliner espouliner esquicher esquimauter
 esquisser esquiver essaimer essarder essarmenter essarter esseimer essemiller
 essentialiser esseuler essimer essimpler essorer essoriller essoucher
 estafilader estamper estampiller ester esthétiser estimer estiver estocader
 estomper estoquer estrapader estroper euphoriser européaniser européiser
 exacerber exalter examiner excardiner excaver exceller excentrer excepter
 exciser exciter exclamer excrémenter excursionner excuser exempter exhaler
 exhiber exhorter exhumer exiler existantialiser existentialiser exister
 exorbiter exorciser exostoser expanser expansionner expectorer expertiser
 explanter expliciter expliquer exploiter explorer exploser exponctuer exporter
 exprimer expulser expérimenter exsuder exsuffler exterminer externaliser
 extorquer extrader extradosser extrapoler extraposer extravaguer extravaser
 extrémiser extrêmiser exténuer extérioriser exulter exécuter fabricoter
 fabuler facetter faciliter factionner factoriser facturer fader fagoter
 failler fainéanter faisander falquer faluner familiariser fanatiser faner
 fanfaronner fanfrelucher fantasmer faonner faradiser farandoler farauder
 farfouiller farguer fariboler fariner farnienter farter fasciner fasciser
 faseyer faséyer fatiguer fauberder fauberter faucarder faucher fauciller
 fauder faufiler fausser fauter favoriser faxer fayoter fayotter façonner
 feinter fellationner fendiller fenestrer fenêtrer ferler fermenter fermer
 ferralitiser ferrer ferrouter ferruginer ferruginiser fertiliser fesser
 festonner feuiller feuilletiser feuilletonner feuilloler feuillurer feuler
 fiabiliser fibrer fibriller fibuler ficher fidéliser fieffer fienter fifrer
 figurer filer filialiser filiforer filigraner filleriser fillonner filmer
 filoguider filouter filtrer finaliser finlandiser fionner fioriturer
 fissionner fissurer fistuliser fitter fixer flacher flageller flageoler
 flairer flamandiser flamber flammer flancher flanquer flaquer flasher flatter
 flemmarder flemmer fletter fleurdeliser fleurer fleuronner flibuster
 flinguer flinquer flipper fliquer flirter floconner floculer floquer florer
 flouer fluater fluber fluctuer fluer fluidiser fluorer fluoriser fluorurer
 flytoxer flâner flânocher flânoter flâtrer flûter focaliser foirer foisonner
 folichonner folioter folâtrer fomenter fonctionnaliser fonctionnariser
 fonder forer forfaitariser forfaitiser forhuer forligner formaliser formater
 formoler formuer formuler formyler forniquer forpaiser fossiliser fouailler
 fouiller fouiner foularder fouler foulonner fourailler fourber fourcher
 fourguer fourmiller fourrer foéner foëner fractionner fracturer fragiliser
 fraiser framboiser franchiser franciser franfrelucher fransquillonner frapper
 fraterniser frauder fredonner freiner frelater fretter fricoter frictionner
 friller frimater frimer fringaler fringuer friper friponner friseliser friser
 frisoter frisotter frissonner fritter froisser fronder froquer frotailler
 frotter frouer froufrouter fructidoriser fruiter frusquer frustrer frégater
 frétiller frôler fuguer fulgurer fulminer fumailler fumer fumeronner fumoter
 funester furibonder fuser fusiller fusiner fusionner futiliser fâcher
 fébriliser féconder féculer fédéraliser féeriser féliciter féminiser fénitiser
 fétichiser fêler fêter gaber gabionner gadgétiser gafer gaffer gagner gainer
 galber galer galipoter galler galocher galonner galoper galopiner galvaniser
 galvauder gamahucher gambader gambergeailler gambeyer gambiller gaminer
 ganser ganter garder gardienner garer gargariser gargoter gargouiller
 garrotter garçonner gasconner gaspiller gastrectomiser gastrotomiser gauchiser
 gaufrer gauler gauloiser gausser gaver gazer gazonner gazouiller gemeller
 gendarmer gerber germaniser germer germiner gesticuler ghettoïser giberner
 gifler gigoter giguer ginginer ginguer girer gironner girouetter givrer
 glairer glaiser glander glandouiller glaner glavioter glaviotter glisser
 globuliser gloser glottaliser glottorer glouglouter glousser gloutonner gluer
 glycériner gobeloter gober gobichonner godailler goder godiller godronner
 goinfrer golfer gominer gommer goménoler gonder gondoler gonfler gorgeonner
 gouacher gouailler goualer gouaper goudronner goujonner goupiller goupillonner
 gourbiller gourer gourmander gourmer gournabler goutter gouverner goûter
 gracieuser graciliser grader graduer graffigner graffiter grafigner grailler
 grainer graisser grammaticaliser graniter granitiser granuler graphiquer
 grappiller grappiner grasseyer graticuler gratiner gratouiller gratter
 grattouiller graver gravillonner graviter gravurer grecquer grediner greffer
 grenader grenailler grenouiller grenter greviller gribouiller griffer
 grigner grignoter griller grimer grimper grincher gringotter gringuer gripper
 griser grisoler grisoller grisonner grivoiser grogner grognonner gronder
 grouiner grouper groupusculariser gruauter gruer grusiner gruter gréciser
 grésillonner grêler guerdonner guetter gueuler gueuletonner gueusailler
 guider guidonner guigner guignoler guiller guillocher guillotiner guimper
 guinder guiper guirlander guitariser guniter gutturaliser guêper guêtrer
 gypser gyrer gâcher gégèner géhenner gélatiner gélatiniser géliver gémeller
 génoper généraliser géométriser gêner gîter gödeliser gödéliser habiliter
 habiter habituer hacher hachurer haleiner haler halluciner halogéniser halter
 hancher handicaper hanner hannetonner hanter happer haranguer harder
 harnacher harnaquer harpailler harper harpigner harponner hasarder haubaner
 haver helléniser herbeiller herber herboriser hercher herscher herser heurter
 hiberniser hier hindouiser hispaniser hisser historialiser historiciser
 histrionner hiverner hivériser hiérarchiser hocher hogner hominiser
 homologuer homopolymériser homosexualiser hongrer honorer horizonner
 hormoner horodater horripiler hospitaliser hotter houblonner houer houler
 hourailler hourder houspiller housser houssiner hucher huer huiler hululer
 humecter humer hurler hurtebiller hussarder hutter hybrider hydrater
 hydrocraquer hydrocuter hydrodésalkyler hydrodésulfurer hydroformer
 hydrolyser hydrophiliser hydroplaner hydropneumatiser hydroraffiner hydroxyler
 hyperboliser hypercentraliser hypermédiatiser hyperorganiser hyperpolariser
 hyperspécialiser hypnotiser hystériser hâbler hâler hébraïser héliporter
 hélitreuiller hématoser hémiacétaliser hémidécérébeller hémodialyser hémolyser
 hépatectomiser hépatiser hérisser hérissonner hériter héroïser hésiter hôler
 iconiser idiotiser idolâtrer idéaliser idéologiser ignorer illettrer illimiter
 illusionner illustrer illuter imaginer imbiber imbriquer imiter immatriculer
 immigrer imminer immobiliser immoler immortaliser immuniser impacter impaluder
 impatroniser imperméabiliser impersonnaliser implanter impliquer implorer
 implémenter importer importuner imposer impressionner imprimer improuver
 impréciser impulser imputer impétiginiser inactiver inalper inaugurer incaguer
 incardiner incarner incidenter inciser inciter incliner incomber incommoder
 incriminer incruster incrémenter incuber inculper inculquer incurver indaguer
 indenter indexer indianiser indigestionner indigner indiquer indisposer
 individuer indoloriser indurer industrialiser indéfiniser indéterminer
 infantiliser infatuer infecter infester infibuler infiltrer infirmer influer
 informer infroissabiliser infuser inféoder inférioriser ingurgiter inhaler
 inhumer initialer initialiser injecter innerver innocenter innover inoculer
 inquarter insaliver insculper insensibiliser insinuer insister insoler
 insonoriser inspecter inspirer installer instantanéiser instaurer instiguer
 instituer institutionnaliser instrumentaliser instrumenter insuffler
 insulter insupporter insécuriser inséminer intailler intellectualiser intenter
 intentionner intercaler intercepter interconnecter interféconder interjecter
 interligner interloquer internaliser internationaliser interner interpeller
 interpolliniser interposer intersecter intersectionner interviewer intimer
 intituler intoxiquer intrigailler intriguer intriquer introjecter introniser
 intuber intuiter intuitionner intéresser intérioriser inutiliser invaginer
 invectiver inventer inverser investiguer inviter involuer invoquer inégaliser
 iodler iodurer ioniser iouler iraniser iriser ironiser irriguer irriter
 irruer irréaliser islamiser isoler isomériser italianiser italiser ivrogner
 jabler jaboter jacter jaffer jalonner jalouser jamber jambonner japonaiser
 japonner japper jardiner jargauder jargonner jaroviser jaser jasper jaspiner
 jazzer jerker jeûner jobarder jodler jogger joggliner jointer joncher jongler
 jouailler joualiser jouer journaliser jouter jouxter jubiler jucher judaïser
 juguler jumboïser jumper juponner jurer juter juxtaposer jérémiader jésuiter
 kaoliniser kidnapper klaxonner knockouter knouter kératiniser labelliser
 labourer labéliser lactoniser lactoser laguner lainer laisser laitonner
 lambrequiner lambrisser lameller lamenter lamer laminer lamper lancequiner
 languetter langueyer lansquiner lanter lanterner lantiponer lantiponner laper
 lapider lapiner lapiniser laquer larder lardonner larguer larmer larronner
 latiniser latter latéraliser latéritiser laudaniser laurer laver lavougner
 laïciser laïusser lemmatiser lenter lessiver lester lettrer leurrer levrauder
 levurer lexicaliser liaisonner liarder libeller libertiner libéraliser licher
 lichéniser liciter lifter ligaturer ligner ligoter liguer limander limaçonner
 limiter limoner limousiner lingoter linguer linotyper linéamenter linéariser
 liquider liser liserer lisser lister lisérer liteauner liter lithochromiser
 litonner litrer littératurer livrer lober lobotomiser localiser locher
 lofer loffer lombaliser loquer lorgner lotionner loucher louer louper lourder
 louver lover lucher luncher luner lunetter lustrer luter lutiner lutter
 luxer lyncher lyophiliser lyrer lyriser lyser lâcher léchonner léchotter
 légaliser légender légitimer lépariniser lésiner léviter lézarder macadamiser
 machiner macler macquer maculer madraguer madrigaliser madériser maffioter
 magasiner magner magnétiser magnétoscoper magouiller magyariser mailer mailler
 maillonner majorer malaxer malléabiliser malléiner malter maltraiter malverser
 manchonner mandater mander mandriner mangeailler mangeotter manifester
 manipuler mannequiner manoeuvrer manoquer manquer mansarder manualiser
 manufacturer manufacturiser manutentionner maquer maquereauter maquereller
 maquiller marauder marbrer marchandailler marchander marchandiser marcher
 margauder marginaliser marginer margoter margotter mariner marivauder marmiter
 marmoriser marmotter marner maronner maroquiner marotiser maroufler marquer
 marrer marronner marsouiner marsupialiser martiner martingaler martingaliser
 marxiser masculiniser masquer massacrer masselotter massicoter mastiquer
 mastériser matcher mater maternaliser materner materniser mathématiser
 matriculer matter maturer matérialiser maximaliser maximer maximiser mazer
 mazurker maçonner maîtriser membrer mendigoter menotter mensualiser mensurer
 mentholer mentionner menuiser mercantiliser merceriser mercurer merder
 meringuer merliner merlonner mesurer meubler meugler meuler meuliériser
 miauler michetonner microdoser microficher microfilmer micromanipuler
 microniser microplisser microprogrammer microsabler microsouder microter
 mignoter migrainer migrer mijoter mildiouser militariser militer millerander
 millésimer mimer minauder miner miniaturer miniaturiser minimaliser minimiser
 minotauriser minuter minéraliser miraculer mirailler mirer miroiter miser
 mitadiner miter mithridater mithridatiser mitonner mitrailler mixer mixter
 mobiliser modaliser moderniser moduler modéliser modérantiser moellonner
 mofler moirer moiser moissonner molarder molariser molester moletter mollarder
 molletter moléculariser monarchiser mondaniser monder mondialiser moniliser
 monomériser monophtonguer monopoler monopoliser monoprogrammer monosiallitiser
 monotoniser monseigneuriser monter montrer monumentaliser monétariser
 moquer moquetter morailler moraliser mordailler mordiller mordillonner
 mordoriser morfailler morfaler morfiler morfler morganer morguer morner
 morplaner mortaiser mosaïquer motionner motiver motoriser motter moucharder
 moucheronner moufeter mouffer mouffeter moufler moufter mouiller mouler
 moulurer mouronner mousseliner mousser moutarder moutonner mouvementer mouver
 moyetter mucher muer muloter multilatéraliser multinationaliser multipler
 multiprogrammer municipaliser munitionner murailler murer murmurer musarder
 muser musiquer musquer musser muséaliser muter mutiler mutiner mutualiser
 myloniser mylonitiser myorelaxer myristiquer myrrher mysticiser myéliniser
 mâchiller mâchonner mâchoter mâchouiller mâchurer mâter mâtiner mécaniser
 mécontenter médailler médeciner médiatiser médicaliser médicamenter médiser
 méduser mégisser mégoter mélancoliser méliniter mélodramatiser mémoriser
 mépriser mériter mésarriver mésestimer mésinformer mésuser métaboliser
 métalliser métamictiser métamorphiser métamorphoser métamériser métaphoriser
 métempsychoser méthaniser méthyler métisser métriser météoriser mêler nacrer
 naniser napalmer napalmiser naphtaliner napper napperonner narcoser narcotiser
 narrativiser narrer nasaliser nasarder nasillarder nasiller nasillonner
 nationaliser natter naturaliser navaliser navigabiliser naviguer navrer
 nerver nervurer neuraliser neuroleptiser neurotiser neutraliser neutrodyner
 nicher nicotiniser nider nieller nigauder nimber nipper niquer nitrater nitrer
 nitroser nitrurer nobéliser noctambuler noliser nomadiser nombrer
 nominaliser nominer nommer nonupler noper nopper nordester nordouester
 normander normandiser normer notabiliser noter nouer nover noyauter
 nuer nuiter numériser numéroter nupler nymphoser néantiser nébuliser
 nécroser négativer néoformer néolithiser néologiser néosynthétiser
 néphrostomiser névroser objecter objectiver objurguer obliquer obnubiler
 observer obstiner obstruer obturer occasionner occidentaliser occulter occuper
 ocrer octupler océaniser odorer odoriser oedipianiser oedématiser oeillader
 oeuvrer offenser officialiser offusquer oligomériser oligopoliser olinder
 olofer oloffer ombiliquer ombrer onder onduler opaliser operculer opiner
 opposer oppresser opprimer opter optimaliser optimiser oraliser orbiter
 ordonner organiciser organiser organsiner orientaliser orienter originer
 ornementer orner orthogonaliser oscariser osciller oser ossianiser ostraciser
 ouatiner ouiller ouralitiser ourler outer outiller outrecuider outrer ouvrer
 ovaliser ovariectomiser ovationner ovuler oxycouper oxyder oxytoniser ozoner
 packer pacotiller pacquer pacser pactiser paddocker padouer paganiser pageoter
 pagnoter paillarder paillassonner pailler paillonner paissonner pajoter
 paladiner palancrer palangrer palanquer palataliser palatiser paletter
 palissader palisser palissonner palmer paloter palper palpiter palucher
 panader pancarter paner paniquer panneauter panner pannetonner panoramiquer
 panser pantiner pantomimer pantoufler paoner paonner papelarder papillonner
 papoter papouiller paquer paraboliser parachuter parader parafer paraffiner
 paralléliser paralyser paramétriser parangonner parapher paraphraser parasiter
 parceller parcelliser parcheminer parcoriser pardonner parementer
 parer paresser parfiler parfumer parisianiser parjurer parkériser parlementer
 parloter parlotter parquer parrainer participer particulariser partitionner
 partouzer pasquiner passefiler passementer passepoiler passeriller passionner
 pasteller pasteuriser pasticher pastiller pastoriser patafioler pateliner
 paternaliser paterner pathétiser patienter patiner patoiser patouiller
 patrociner patronner patrouiller patter paumer paupériser pauser pavaner paver
 peaufiner pectiser peigner peiner peinturer peinturlurer pelaner pelauder
 pelleverser pelliculer peloter pelotonner pelucher pelurer pencher pendeloquer
 pendouiller penduler penser pensionner peptiser peptoniser percaliner percher
 percoler percuter perdurer perfectionner perforer performer perfuser perler
 permanenter permaner permuter perméabiliser peroxyder perpétuer
 perreyer perruquer persifler persiller persister personnaliser persuader
 persécuter perturber pervibrer pester peupler pexer phagocyter phalangiser
 philosophailler philosopher phlegmatiser phlogistiquer phlébotomiser
 phonétiser phosphater phosphorer phosphoriser phosphoryler photoactiver
 photocomposer photograver photomonter photophosphoryler photopolymériser
 photoïoniser phraser phéniquer phénoler phényler piaffer piailler pianomiser
 piauler pickler picocher picoler picorer picoter picouser picouzer picrater
 pictonner picturaliser pidginiser pierrer pieuter pifer piffer piffrer
 pigmenter pigner pignocher pignoler piler piller pilloter pilonner piloter
 pinailler pinceauter pindariser pinter pinçoter piocher pionner piotter piper
 piqueniquer piquer piquetonner piquouser piquouzer pirater pirouetter piser
 pissoter pissouiller pister pistoler pistonner pitancher pitcher piter
 pituiter pivoter piédestaliser piétiner placarder placardiser plafonner
 plainer plaisanter plamer plancher planer planquer planter planétariser
 plaquer plasmolyser plastiquer plastronner platiner platiniser platoniser
 pleurailler pleuraliser pleurer pleurnicher pleuroter pleuviner pleuvioter
 pleuvoter plisser plissoter plomber ploquer plotiniser plouter ploutrer
 plumarder plumer pluraliser pluviner pluvioter plâtrer plébisciter pocharder
 pochetronner pochtronner poculer podzoliser poignarder poigner poiler pointer
 poinçonner poireauter poirer poiroter poisser poitriner poivrer poivroter
 poldériser polissonner politicailler politiquer politiser polker polliciser
 polliniser polluer poloniser polychromer polycontaminer polygoner polygoniser
 polyploïdiser polytransfuser polyviser polémiquer pommader pommer pomper
 ponctionner ponctuer ponter pontiller populariser poquer porer porphyriser
 porter porteuser portionner portraicturer portraiturer poser positionner
 possibiliser postdater poster posticher postillonner postposer postsonoriser
 postuler postérioriser potabiliser potentialiser poter poteyer potiner poudrer
 pouiller pouliner pouloper poulotter pouponner pourpenser pourprer poussailler
 pousser poutser poétiser poêler praliner pratiquer presser pressurer
 primariser primer primherber printaniser prioriser priser prismatiser prismer
 priver probabiliser problématiser processionner proclamer procrastiner
 prodiguer profaner professer professionnaliser profiler profiter programmer
 prohiber prolétariser promotionner promulguer pronominaliser pronostiquer
 prophétiser propoliser proportionner proposer propulser propylitiser prosaïser
 prosterner prostituer prostrer protestaniser protestantiser protester
 protoner prototyper protracter protéiner protéolyser prouter prouver
 proverbialiser provigner provincialiser provisionner provoquer proéminer
 prussianiser préaccentuer préadapter préallouer préassembler préaviser
 précautionner préchauffer préchauler précipiter préciser préciter précompter
 préconditionner préconfigurer préconiser préconstituer précoter prédater
 prédiffuser prédilectionner prédiquer prédisposer prédominer prédécouper
 préemballer préempter préencoller préenregistrer préenrober préexaminer
 préfabriquer préfaner préfigurer préfixer préformater préformer préformuler
 préfritter préimprimer préinstaller prélaquer prélaver préliber préluder
 prémonter prémédiquer préméditer prénommer préoccuper préopiner préordonner
 préozoner préparer préposer préscolariser présensibiliser présenter préserver
 présider présignaliser présonoriser préstructurer présumer présupposer
 présélectionner prétailler prétanner prétester prétexter prétintailler
 prévariquer préverber prêchailler prêcher prêter prôner pschuter psychanalyser
 psychologiser psychotiser publiciser pucher puddler puer puiser pulluler
 pulser pulvériser punaiser puncturer pupiniser pupuler puriner puruler
 puter putoiser putter puériliser pyramider pyrograver pyrolyser pyrrhoniser
 pâtonner pâturer pèleriner pébriner pécher pécloter pédaler pédanter
 pédiculiser pédicurer pédimenter péjorer péleriner pénaliser pénéplaner
 péricliter périmer périodiser périphraser périphériser péritoniser pérorer
 pétarader pétarder pétiller pétitionner pétocher pétouiller pétrarquiser
 pétuner pêcher quadriller quadripolariser quadrupler quarderonner quarrer
 quartiler quereller querner questionner queurser queuter quiller quimper
 quitter quoailler quotter quémander quêter rabaisser rabaner rabanter
 rabibocher rabioter raboter rabouiller rabouler rabouter rabreuver rabrouer
 raccastiller raccommoder raccompagner raccorder raccoutrer raccoutumer
 rachalander racher raciner racketter racler racoler raconter racoquiner
 racémiser radariser rader radicaliser radiner radioactiver radiobaliser
 radiocommander radioconserver radiodiffuser radiodétecter radioexposer
 radiolocaliser radiopasteuriser radiosonder radiostériliser radiotéléphoner
 radoter radouber rafaler raffermer raffiler raffiner raffluer raffoler
 rafistoler rafler ragoter ragoûter ragrafer raguer raguser raiguiser railler
 rainurer raisonner rajouter rajuster ralinguer raller rallumer ramailler
 ramarder ramarrer ramastiquer rambiner ramender ramer rameuter ramoner ramper
 ramser rancarder randomiser randoniser randonner randonniser ranimer rançonner
 rapapilloter rapatronner raper rapetisser rapiater rapiner rappareiller rapper
 rapporter rapprivoiser rapprocher rapprovisionner rapprêter rapsoder raquer
 raser rassembler rassoter rassurer ratatiner rater ratiboiser ratiner
 rationaliser rationner ratisser ratonner rattacher rattaquer rattirer
 raturer raucher raugmenter rauquer ravaler ravauder ravigoter raviner raviser
 raviver rayonner rebachoter rebadigeonner rebaigner rebaiser rebaisoter
 rebalader rebaliser rebancher rebander rebaptiser rebaratiner rebarber
 rebarbouiller rebarder rebarrer rebarricader rebasculer rebavarder rebecquer
 rebeller rebeurrer rebiffer rebiner rebioler rebipolariser rebiquer rebisouter
 rebizouter reblackbouler reblesser reblinder rebloquer rebobiner reboiser
 rebombarder rebomber reborder rebosser rebotter reboucher reboucler
 reboulonner rebourrer reboursicoter rebousculer rebouter reboutonner reboxer
 rebraguetter rebrancher rebraquer rebricoler rebrider rebriguer rebriller
 rebrocher rebroder rebronzer rebrosser rebrouiller rebrousser rebrûler
 rebuffer rebuller rebureaucratiser rebuter rebâcher rebâcler rebâfrer
 rebâillonner rebécoter rebétonner rebêcher rebûcher recacher recadrer
 recalaminer recalculer recaler recalfater recalfeutrer recalibrer recalquer
 recamoufler recamper recanaliser recanner recanonner recaoutchouter
 recapoter recaptiver recapturer recaractériser recarburer recarder recaresser
 recasquer recataloguer recatégoriser recauser recavaler recaver receler
 recensurer recentraliser recentrer receper recercler recerner rechagriner
 rechamailler rechambouler rechanter rechantonner rechaper rechaptaliser
 recharpenter rechauffer rechauler rechaumer rechausser rechercher rechiader
 rechiffrer rechigner rechiper rechristianiser rechromer rechuter recibler
 recirculer recirer reciter recliquer recloisonner reclouer reclôturer
 recoder recogner recoiffer recollaborer recollecter recoller recolliger
 recoloniser recolorer recolporter recoltiner recombiner recommander
 recommenter recommercialiser recommissionner recommuniquer recommémorer
 recompartimenter recompiler recomplimenter recompliquer recomploter recomposer
 recompter recompulser reconcrétiser recondamner recondenser reconditionner
 reconfesser reconfigurer reconfirmer reconfisquer reconfronter reconjuguer
 reconsacrer reconseiller reconserver reconsigner reconsoler reconsolider
 reconspirer reconstater reconstituer reconsulter recontacter reconter
 recontingenter recontinuer recontracter recontrecarrer recontrer recontribuer
 reconverser reconvoquer recoordonner recoquiller recorder recorroborer recoter
 recoucher recouillonner recouler recoulisser recouper recouponner recourber
 recourtiser recouvrer recoïncider recracher recraquer recravater recreuser
 recrier recristalliser recritiquer recroiser recroquer recroqueviller
 recruter recréer recuisiner reculer reculotter recultiver recycler recâbler
 recéper redaller redamer redanser redater redemander redesserrer redessiner
 redialoguer redicter rediffuser redimensionner rediminuer rediscerner
 redisjoncter redisloquer redispenser redisperser redisposer redisputer
 redistiller redistinguer redistribuer rediviser redominer redompter redonder
 redoper redorer redorloter redoser redoter redoubler redouter redresser
 redynamiser redéballer redébarbouiller redébarquer redébaucher redébiner
 redébloquer redébobiner redéborder redéboucher redébourser redébouter
 redébrancher redébrouiller redébroussailler redébudgétiser redébureaucratiser
 redécaisser redécaler redécalquer redécanter redécaper redécapoter
 redécerner redéchausser redéchiffrer redéchirer redécider redéclarer
 redécliner redécoder redécoiffer redécoller redécoloniser redécolorer
 redécompter redéconcentrer redéconnecter redéconner redéconseiller redécorer
 redécouler redécouper redécrocher redécrypter redéculotter redéfausser
 redéfricher redéfriper redéfriser redéfroisser redégivrer redégonfler
 redégotter redégringoler redégrouper redéjeuner redélimiter redélivrer
 redémarrer redéminer redémissionner redémobiliser redémocratiser redémonter
 redémêler redénicher redénombrer redénouer redépanner redépeigner redépenser
 redéplisser redéporter redéposer redépouiller redérailler redérober redéserter
 redésirer redésister redétacher redétailler redétecter redéterminer redéterrer
 redétériorer redévaler redévaliser redévaloriser redévaluer redévaster
 redévisser redévoiler redîner refabriquer refacturer refamiliariser
 refarter refasciser refaucher refaufiler refavoriser refaçonner refermer
 refeuiller reficher refidéliser refiler refilmer refiltrer refiscaliser
 reflamber reflancher reflanquer reflotter refluer refluxer refoirer
 refonder reforer reforester reformaliser reformater reformer reformuler
 refouler refourgonner refourrer refranchiser refranciser refrapper
 refringuer refriper refriser refrogner refroisser refrotter refréner
 refuguer refumer refuser refâcher reféliciter reféminiser refêter regaffer
 regalber regaloper regambader regarder regarer regazonner regerber regermer
 regimber registrer reglisser regober regommer regonfler regoudronner regourer
 regoûter regrader regratter regraver regreffer regretter regriffer regriller
 regrogner regronder regrouper regrêler regueuler regâcher rehasarder rehausser
 rehiérarchiser rehomologuer rehospitaliser rehériter rejalonner rejetonner
 rejouer relabourer relaisser relarguer relater relatiniser relationner
 relatter relaver relaxer relifter relimer reliquider relisser relocaliser
 relouer relouper reluquer relustrer relutter relâcher relégender relégitimer
 remailer remailler remajorer remaltraiter remandater remanifester remanoeuvrer
 remaquiller remarchander remarcher remarquer remartyriser remasquer
 remastiquer remasturber remastériser remaçonner remaîtriser remballer
 rembarrer rembaucher rembiner remblaver rembobiner remborder rembourrer
 remboîter rembucher remembrer rementionner remesurer remeubler remilitariser
 reminer reminuter reminéraliser remiser remixer remmailler remmailloter
 remmouler remobiliser remoderniser remonter remontrer remonétiser remoquetter
 remotiver remotoriser remoucher remouiller remouler rempailler remparer
 remplumer rempocher rempoisonner rempoissonner remporter rempoter remprisonner
 remuer remurmurer remuscler remâcher remédicaliser remémorer remêler renarder
 renatter renaturaliser renauder renaviguer rencaisser rencarder renchausser
 rencogner rencoller rencontrer rencoquiller rencorser rendetter rendosser
 renfaîter renfermer renfiler renflammer renfler renflouer renformer
 renfourner renfrogner rengainer rengraisser rengrener rengréner renifler
 renommer renoper renormaliser renoter renouer renquiller renseigner renserrer
 rentamer renter rentoiler rentortiller rentraîner rentrer renucléariser
 renvelopper renvenimer renverser renvider renvoler renâcler repaginer repairer
 repapilloter reparapher repardonner reparer reparler reparticiper repatiner
 repaumer repaver repeigner repeinturer repencher repenser repercuter
 reperforer reperméabiliser reperturber repeupler rephosphorer repiler repiller
 repiloter repiocher repiquer repirater repisser repistonner replacarder
 replaider replaisanter replanquer replanter replaquer replastiquer repleurer
 repleuvoter replisser replomber replâtrer repointer repoisser repoivrer
 repolitiser repolluer repomper reponchonner reponctionner repopulariser
 reposer repositionner repositiver repostuler repoudrer repousser repratiquer
 repriser reprivatiser reprocher reproclamer reprofaner reprofiler reprofiter
 reprogresser reprohiber reproposer repropulser reprouver reprovincialiser
 repréparer représenter représider reprêcher reprêter repter repuiser
 repéter repétitionner repêcher requadriller requestionner requiller requinquer
 requêter rerespirer resabler resaboter resaccader resaler resaluer resaper
 resauter resavonner rescaper resceller rescinder reseller resensibiliser
 resiffler resignaler resigner resituer resocialiser resoigner resolliciter
 resouper respectabiliser respecter respirer responsabiliser respéculer
 ressaigner ressaler ressangler ressauter ressembler resserrer ressouder
 ressusciter restabiliser restatuer restaurer rester restituer restoubler
 resuccomber resucrer resulfater resuppurer resurchauffer resyllaber
 resympathiser resynchroniser resyndicaliser resyndiquer resélectionner
 retacher retailler retanner retaper retapisser retarder retarifer retaxer
 reterser retester rethéâtraliser retimbrer retirer retisser retomber retoquer
 retortiller retorturer retoucher retouper retourner retousser retrafiquer
 retrancher retransborder retransformer retransfuser retransiter retranspirer
 retransporter retransposer retransvaser retravailler retraverser retraîner
 retricher retricoter retrifouiller retrimbaler retrimballer retriompher
 retriturer retromper retrotter retrouer retrousser retrouver retruander
 retuer returbiner retéléphoner retéléviser retémoigner revacciner revalider
 revalser revancher revasculariser revendiquer reventer reverbaliser revercher
 reverser revider revigorer revirer reviser revisionner revisiter revisser
 revoler revolvériser revoter revriller rewriter rhabiller rhabiter rhabituer
 rhumer rhétoriquer ribauder ribler riblonner riboter ribouldinguer ribouler
 ricocher rider ridiculiser riduler riffauder rifler rigoler rimailler rimer
 ringardiser rinker rioter ripailler riper ripoliner riposter riser risquer
 ristourner ritter ritualiser rivaliser river rivotter rober robinsonner
 rocailler rocher rocker rocouer rocquer roder rogner rognonner romaniser
 ronchonner ronder ronfler ronfloter ronflotter ronronner ronsardiser ronéoter
 roquer roser rosser rossignoler roter rotomouler rouanner roublarder roucouer
 roucouyer rouer rouiller roulader rouler roulotter roupiller rouscailler
 roussiller roussoter rouster rousturer router routiner rubaner rubriquer
 rudenter ruer ruginer ruiler ruiner ruminer rupiner ruraliser rurbaniser ruser
 russiser rustiquer rutiler rythmer râbler râler râloter râper réabdiquer
 réaborder réabouter réabreuver réabriter réabsenter réabsorber réaccaparer
 réaccepter réaccidenter réacclimater réaccorder réaccoster réaccoutumer
 réaccuser réachalander réacheminer réacquitter réactionner réactiver
 réadapter réadditionner réadministrer réadmonester réadonner réadopter
 réaffecter réaffermer réafficher réaffiler réaffirmer réaffronter réaffûter
 réagglutiner réaggraver réagrafer réagresser réaiguiller réaiguillonner
 réaimanter réaimer réajourner réajuster réalcooliser réalerter réaligner
 réaliser réallaiter réallouer réallumer réamarrer réamender réamidonner
 réanalyser réanastomoser réanimer réannexer réannoter réapaiser réapostropher
 réappliquer réapposer réapprivoiser réapprouver réapprovisionner réappréhender
 réapurer réarchitecturer réargenter réargumenter réarmer réarnaquer réarpenter
 réarroser réarrêter réarticuler réasphalter réaspirer réassaisonner
 réassigner réassister réassumer réassurer réastiquer réattaquer réattiser
 réauditionner réaugmenter réautomatiser réautoriser réavaler réavaliser
 rébellionner récapituler réceptionner réchapper réchauffer réchelonner
 réciproquer réciter réclamer récliner récoler récolliger récolter récompenser
 récrier récriminer récréer récurer récuser rédimer réeffectuer réemballer
 réembaucher réembobiner réembourber réembouteiller réemboîter réembrigader
 réemmailloter réemmancher réemmerder réemmêler réemparer réempiler réempocher
 réempoisonner réempoissonner réemprisonner réemprunter réempêcher réempêtrer
 réencaisser réencaustiquer réencercler réenchaîner réenchevêtrer réenchâsser
 réenclencher réencoder réencombrer réendetter réendosser réenfiler réenflammer
 réenfourcher réenfourner réengendrer réenglober réengouffrer réengraisser
 réenjamber réenliser réenquêter réenregistrer réenrhumer réenrouler
 réentamer réentartrer réenterrer réenthousiasmer réentortiller réentourer
 réentrer réenvelopper réenvenimer réenvoler réenvoûter réescalader réescamoter
 réescorter réestimer réexalter réexaminer réexcuser réexhiber réexhorter
 réexpertiser réexpirer réexpliciter réexpliquer réexploiter réexplorer
 réexposer réexprimer réexpulser réexpérimenter réextrader réexécuter
 réflectoriser réflexionner réflexiviser réformer réfracter réfréner réfuter
 régater régenter régimer régionaliser réglementer régresser régulariser
 régurgiter réhabiliter réhabiter réhabituer réharmoniser réhomologuer
 réhydrater réillustrer réimaginer réimbiber réimbriquer réimperméabiliser
 réimpliquer réimplorer réimporter réimportuner réimposer réimprimer
 réimpulser réimputer réincarner réinciser réincomber réincorporer réincruder
 réincuber réinculper réinculquer réindemniser réindexer réindustrialiser
 réinfester réinfiltrer réinformatiser réinféoder réingurgiter réinhiber
 réinjecter réinsister réinsonoriser réinspecter réinspirer réinstaller
 réinstituer réintenter réintercaler réintercepter réinterner réinterviewer
 réintituler réintéresser réinventer réinviter réislamiser rénetter rénover
 réobserver réobstruer réobturer réoccuper réorchestrer réordonner réorganiser
 réoxyder réparer répartonner répercuter répliquer réprimander réprimer
 républicaniser répugner réputer répétailler répéter réquisitionner réserver
 résigner résiner résister résonner résorber résulter résumer résupiner rétamer
 rétorquer rétracter rétribuer rétrodiffuser rétrograder rétromorphoser
 rétroréflectoriser rétroréguler rétroverser réunionner réusiner réutiliser
 réveillonner réviser révolter révolutionnariser révolutionner révolvériser
 révulser réécarter rééchafauder rééchelonner rééchouer rééclairer rééconomiser
 réécourter réécouter réécrouer réédicter rééditer rééduquer rééjecter
 réélaguer réémigrer réémonder réénergétiser réépargner réépiler rééplucher
 rééquilibrer rééquiper réétaler réétamer réétatiser réétoffer réévaluer
 rêner rêver rôdailler rôder rôler sabbatiser sabler sablonner saborder saboter
 sabrer saccader sacchariner sacquer sacraliser sacrer sadiser safariser
 saietter saigner sailler saisonner salabrer saler salicyler saligoter saliner
 saliver salonner saloper salpêtrer salpêtriser saluer sanctionner sanctuariser
 sanforiser sangler sangloter sanskritiser saouler saper saquer sarabander
 sarmenter sarper sarrasiner sarter sataner sataniser satelliser satiner
 satoner satonner saturer satyriser saucissonner saumoner saumurer sauner
 saurer saussuritiser sauter sautiller sauvegarder sauver savater savonner
 sayetter scalper scandaliser scander scanner scannériser sceller scheider
 scheloter schizophréniser schlaguer schlinguer schlitter schloffer schloter
 schtroumpfer schématiser scientifiser scinder scintiller sciotter scissionner
 scolariser scooper scorer scotcher scotomiser scotomoser scrabbler scraber
 scribler scribouiller scruter scrutiner sculpter scénariser secondariser
 secouer secréter sectionner sectoriser segmenter seiner seller sembler
 sempler senner sensationnaliser sensibiliser sentimentaliser septembriser
 seriner seringuer sermonner serpenter serpentiniser serper serrer sexer
 sexualiser sganarelliser shampoigner shampooiner shampooingner shampouiner
 shunter shérardiser siallitiser siccativer siester siffler siffloter sigler
 signaliser signer silhouetter silicater silicatiser siliciurer siliconer
 siller sillonner siloter similer similiser simonizer simuler sinapiser
 siniser sinistrer sintériser sinuer siphonner siroper siroter situer skipper
 slaviser smasher smiller smocker smurfer sniffer snober sociabiliser
 socratiser soder sodomiser soiffer soigner solariser solder solenniser
 solifluer soliloquer solliciter solmiser solubiliser solutionner solvabiliser
 soléciser somatiser sombrer sommeiller sommer somnambuler somniloquer somnoler
 sonnailler sonner sonoriser sophistiquer sorguer soubresauter souder
 souffler souffroter soufrer souhaiter souiller souillonner souligner
 soupailler souper soupirer soupçonner souquer sourciller sourdiner soussigner
 souter soutirer soviétiser soûler soûlotter spasmer spatialiser spatuler
 sphéroïdiser spilitiser spiraler spiraliser spirantiser spiritualiser spitter
 splénectomiser spléniser sponsoriser sporter sporuler sprinter spécialiser
 squatter squattériser squeezer stabiliser stabuler staffer stagner staliniser
 standoliser stanioler stariser stationner statistiquer statuer stelliter
 stenciler stendhaliser stepper stigmatiser stimuler stipuler stocker stopper
 stresser strider striduler striper stripper striquer stronker strouiller
 strychniser stuquer styler styliser sténoser sténotyper stériliser stéréotyper
 subdiviser subdivisionner subjectiver subjectiviser subjuguer sublimer
 subluxer subminiaturiser subodorer subordonner suborner subsister substanter
 substantiver substituer subsumer subtiliser suburbaniser subventionner
 succomber sucrer suer suffixer suffoquer suggestionner suicider suifer suiffer
 sulfater sulfiniser sulfinuser sulfiter sulfoner sulfurer sulfuriser super
 superposer superviser supplanter supplémenter supporter supposer supprimer
 supputer supérioriser surabonder suraccumuler suractiver suradapter
 surajouter suralcooliser suralimenter suraller suranimer suranner surarmer
 surblinder surbooker surboucher surbriller surbroder surcapitaliser
 surchauffer surcoller surcolorer surcompenser surcomprimer surconsommer
 surcoter surcouper surcreuser surdimensionner surdorer surdoser surdouer
 surdéterminer surdévelopper surencombrer surendetter surentraîner surestimer
 surexhausser surexploiter surexposer surfacturer surfer surficher surfiler
 surfractionner surfrapper surgeonner surgonfler surgreffer surhausser
 surimpressionner surimprimer surindustrialiser suriner surinfecter surinformer
 surjauler surjouailler surjouer surligner surlouer surmoduler surmonter
 surmédicaliser surmédicamenter surnaturaliser surnommer suroxyder surpatter
 surpiquer surplomber surpresser surreprésenter surréserver sursaler sursaturer
 sursimuler sursouffler surstabiliser surstimuler surstocker sursulfater
 surtaxer surtitrer survaloriser surveiller surventer survider survirer
 survolter suréchantillonner surémanciper suréquiper surévaluer susciter
 susseyer sustanter sustenter susurrer suturer suçoter swaper swinguer
 syllaber syllabiser syllogiser symboliser sympathiser symétriser synchroniser
 syncristalliser syndicaliser syndiquer synthétiser syntoniser syphiliser
 sécréter séculariser sécuriser sédentariser sédimenter séjourner sélecter
 sémantiser sémiller séparer séquestrer sérialiser sérénader tabiser tabler
 tabouiser tabuler tacher tacler taconner taguer taillader tailler taler taller
 talonner talquer taluter tambouiller tambouriner tamiser tamponner tangenter
 tanguer taniser tanner tanniser tantaliser taper tapiner tapirer tapiriser
 taponner tapoter taquer taquiner taquonner tarabiscoter tarabuster tararer
 tarder tarer targetter targuer tarifer tarmacadamiser tarter tartiner
 tartrer tartriquer tatillonner tatouer tatouiller tauder tautologiser
 taveller taxer tayloriser tchatcher techniciser techniser technocratiser
 teiller teinter temporiser tempêter tenailler tenonner tensionner tenter
 terminer terrailler terreauder terreauter terrer terriner territorialiser
 terser tertiariser tester testonner texturer texturiser thermaliser thermiser
 thermocoller thermodiffuser thermofixer thermoformer thermopropulser
 thromboser thyroïdectomiser thématiser théologiser théoriser thésauriser
 tictacquer tictaquer tigrer tiller tilloter tillotter tilter timbrer
 tinter tintinnabuler tiquer tirailler tirebouchonner tirefonner tirer tiser
 tisser titaner titaniser titiller titrer titriser tituber titulariser toaster
 toiler toiletter toiser tolstoïser tomater tomber tomer tonitruer tonner
 tontiner tonturer toper topicaliser toquer torchecuter torcher torchonner
 torgnoler toronner torpiller torsader torsiner tortiller tortillonner tortorer
 tosser toster totaliser toucher touer touffer touiller toupiller toupiner
 tourber tourbillonner tourer tourillonner tourmenter tournailler tournaser
 tourner tournevirer tournicoter tourniller tournioler tourniquer toussailler
 toussoter trabouler tracaner trachéotomiser tracter tractionner traficoter
 trafuser trailler traiter tramer trancaner tranchefiler trancher tranquilliser
 transborder transcender transcoder transfecter transfigurer transfiler
 transfuser transgresser transhumer transistoriser transiter translater
 transmuer transmuter transpirer transplanter transporter transposer transsuder
 transvider trapper traquer traumatiser travailler travailloter traverser
 traîner treillisser trekker trembler tremblocher trembloter tremper
 tressauter tresser treuiller trianguler triballer tribouiller tricher
 tricoter trifouiller trigauder trigonaliser triller trimarder trimbaler
 trimer trimestrialiser trimériser tringler trinquer triompher tripatouiller
 triploïdiser tripolisser tripotailler tripoter tripper triquer trisser
 trivialiser trochisquer trognonner trombiner tromboner tromper troncher
 tronçonner tropicaliser troquer trotter trottiner troubler trouer trouiller
 troussequiner trousser trouver truander trucher trucider truculer trueller
 truiter truquer trusquiner truster trébucher tréfiler trélinguer trémater
 trémuler trépaner trépider trépigner trésailler trévirer trôler trôner tuber
 tuberculiniser tuberculiser tubériser tuer tuiler tumultuer tunnelliser
 turboforer turlupiner turluter turquiser tuteurer tuyauter twister tympaniser
 typer typiser tyranniser tâcher tâtonner télescoper télexer télomériser
 télécommander télédiffuser télédébiter télédétecter téléguider téléimprimer
 télélocaliser télémanipuler télématiser télépancarter téléphoner télépiloter
 téléporter télésignaliser téléviser témoigner ténoriser tétaniser tétonner
 tétuer ultrafiltrer ululer uniformiser universaliser upériser urbaniser uriner
 usiner usiter usurper utiliser vacciner vacher vaciller vacuoliser vadrouiller
 vaguer vaigrer vaironner valdinguer valider vallonner valoriser valser vamper
 vandaliser vaniser vanner vanter vantiler vantiller vapocraquer vaporiser
 varander varapper varianter varioliser varloper vasculariser vasectomiser
 vaser vasouiller vassaliser vaticiner vautrer vedettiser veiller veiner
 velter vendiquer venter ventiler ventouser ventriloquer ventrouiller
 verduniser vergner verjuter vermiculer vermiller vermillonner vermouler
 vernisser verrer verrouiller verser vert-de-griser verticaliser vesser vexer
 viander vibrer vibrionner victimer victimiser vider vidimer vieller
 vigiler vignetter vilipender villégiaturer vinaigrer viner vingtupler
 violer violoner virer virevolter virevousser virevouster virginiser virguler
 viroler virtualiser virusser viser visionner visiter visser visualiser
 vitaminer vitaminiser vitrer vitrioler vitrioliser vivisecter vivoter vobuler
 voguer voiler voiser voisiner voiturer volanter volatiliser volcaniser voler
 voltaïser volter voluter voter vouer vousser voyeller voyelliser voûter
 vrillonner vulcaniser vulgariser vulnérabiliser véhiculer vélariser vélivoler
 véroter vétiller vêler warranter wobbuler xéroxer yodiser yodler youyouter
 yoyotter zader zapper zester zieuter zigouiller zigzaguer zinguer zinzinuler
 zipper zoner zonzonner zoomer zozoter zyeuter zéroter ânonner ébarber ébaucher
 éberluer éberner éboguer éborgner ébosser ébotter ébouer ébouillanter ébouler
 ébourgeonner ébouriffer ébourrer ébouser ébousiner ébouter ébouturer ébraiser
 ébranler ébraser ébrauder ébroder ébrouder ébrouer ébrousser ébruiter ébruter
 écacher écaffer écailler écaler écanguer écapsuler écarbouiller écarder
 écarquiller écarter écarver écepper échafauder échaloter échancrer
 échantillonner échanvrer échapper échardonner écharner écharper écharpiller
 échauder échauffer échauler échaumer échelonner écheniller échevetter échigner
 échopper échosonder échouer écimer éclabousser éclairer éclater éclipser
 écloper écluser écobuer écoeurer écoiner écointer écologiser économiser écoper
 écorcher écorer écorner écornifler écosser écouler écourter écouter
 écrabouiller écraminer écraser écrivailler écroter écrouer écrouler écroûter
 écuisser éculer écumer écurer écussonner écôter édenter édicter éditer
 édulcorer éduquer édéniser éfaufiler égailler égaler égaliser égarer égauler
 églomiser égobler égorgiller égosiller égousser égoutter égrainer égraminer
 égrapper égratigner égravillonner égriser égueuler éherber éhouper éjaculer
 éjarrer éjecter éjointer élaborer élaguer élaiter élaver élaïdiser électriser
 électrocuter électrodéposer électrolyser électroner électroniser
 électropuncturer électrozinguer éliciter élider élimer éliminer élinguer
 éloigner élucider élucubrer éluder éluer élégantiser émailler émanciper émaner
 émender émerillonner émeriser émerveiller émeuler émietter émigrer émonder
 émotionner émotter émoucher émousser émoustiller émuler émulsionner émétiser
 énaser énergiser énergétiser énerver éneyer énieller énoliser énoper énouer
 énupler énuquer éoliser épailler épaler épamprer épancher épanner épanouiller
 éparpiller épater épaufrer épauler éperonner épeuler épeurer épierrer
 épigéniser épilamer épiler épiloguer épimériser épiner épingler épisser
 épithétiser éplorer éplucher époiler épointer épointiller époinçonner
 épouffer épouiller époumoner épouser époustoufler épouvanter éprouver épuiser
 épurer épépiner équerrer équeuter équilibrer équiper équipoller équivoquer
 érafler érailler éreinter éroder érotiser éructer érusser établer étaler
 étalonner étamer étamper étancher étançonner étarquer étatiser étaupiner
 éterniser éternuer éthyler éthériser étioler étirer étoffer étoiler étonner
 étouper étoupiller étranger étrangler étraper étremper étrenner étriller
 étriper étriquer étriver étrogner étronçonner étrésillonner étuver
 étêter évacuer évader évaginer évaguer évaltonner évaluer évangéliser évaporer
 évaser éveiller éveiner éventer éventiller éventrer éverdumer éverser évertuer
""".split())