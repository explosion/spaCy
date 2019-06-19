# coding: utf8
from __future__ import unicode_literals


VERBS = set(
    """
 abaisser abandonner abdiquer abecquer abéliser aberrer abhorrer abîmer abjurer
 ablater abluer ablutionner abominer abonder abonner aborder aborner aboucher
 abouler abouter aboutonner abracadabrer abraquer abraser abreuver abricoter
 abriter absenter absinther absolutiser absorber abuser académifier académiser
 acagnarder accabler accagner accaparer accastiller accentuer accepter
 accessoiriser accidenter acclamer acclimater accointer accolader accoler
 accommoder accompagner accorder accorer accoster accoter accoucher accouder
 accouer accoupler accoutrer accoutumer accouver accrassiner accréditer
 accrocher acculer acculturer accumuler accuser acenser acétaliser acétyler
 achalander acharner acheminer achopper achromatiser aciduler aciériser
 acliquer acoquiner acquêter acquitter acter actiniser actionner activer
 actoriser actualiser acupuncturer acyler adapter additionner adenter adieuser
 adirer adjectiver adjectiviser adjurer adjuver administrer admirer admonester
 adoniser adonner adopter adorer adorner adosser adouber adresser adsorber
 aduler adverbialiser aéroporter aérosoliser aérosonder aérotransporter
 affabuler affacturer affairer affaisser affaiter affaler affamer affecter
 affectionner affermer afficher affider affiler affiner affirmer affistoler
 affixer affleurer afflouer affluer affoler afforester affouiller affourcher
 affriander affricher affrioler affriquer affriter affronter affruiter affubler
 affurer affûter afghaniser afistoler africaniser agatiser agenouiller
 agglutiner aggraver agioter agiter agoniser agourmander agrafer agrainer
 agrémenter agresser agricher agriffer agripper agroalimentariser agrouper
 aguetter aguicher aguiller ahaner aheurter aicher aider aigretter aiguer
 aiguiller aiguillonner aiguiser ailer ailler ailloliser aimanter aimer airer
 ajointer ajourer ajourner ajouter ajuster ajuter alambiquer alarmer albaniser
 albitiser alcaliniser alcaliser alcooliser alcoolyser alcoyler aldoliser
 alerter aleviner algébriser algérianiser algorithmiser aligner alimenter
 alinéater alinéatiser aliter alkyler allaiter allectomiser allégoriser
 allitiser allivrer allocutionner alloter allouer alluder allumer allusionner
 alluvionner allyler aloter alpaguer alphabétiser alterner aluminer aluminiser
 aluner alvéoler alvéoliser amabiliser amadouer amalgamer amariner amarrer
 amateloter ambitionner ambler ambrer ambuler améliorer amender amenuiser
 américaniser ameulonner ameuter amhariser amiauler amicoter amidonner
 amignarder amignoter amignotter aminer ammoniaquer ammoniser ammoxyder amocher
 amouiller amouracher amourer amphotériser ampouler amputer amunitionner amurer
 amuser anagrammatiser anagrammer analyser anamorphoser anaphylactiser
 anarchiser anastomoser anathématiser anatomiser ancher anchoiter ancrer
 anecdoter anecdotiser angéliser anglaiser angler angliciser angoisser anguler
 animaliser animer aniser ankyloser annexer annihiler annoter annualiser
 annuler anodiser ânonner anser antagoniser antéposer antérioriser
 anthropomorphiser anticiper anticoaguler antidater antiparasiter antiquer
 antiseptiser anuiter aoûter apaiser apériter apetisser apeurer apicaliser
 apiquer aplaner apologiser aponévrotomiser aponter aposter apostiller
 apostoliser apostropher apostumer apothéoser appareiller apparenter appeauter
 appertiser appliquer appointer appoltronner apponter apporter apposer
 appréhender apprêter apprivoiser approcher approuver approvisionner approximer
 apurer aquareller arabiser araméiser aramer araser arbitrer arborer arboriser
 arcbouter arc-bouter archaïser architecturer archiver arçonner ardoiser
 aréniser arer argenter argentiniser argoter argotiser argumenter arianiser
 arimer ariser aristocratiser aristotéliser arithmétiser armaturer armer
 arnaquer aromatiser arpenter arquebuser arquer arracher arraisonner arrenter
 arrêter arrher arrimer arriser arriver arroser arsouiller artérialiser
 articler articuler artificialiser artistiquer aryaniser aryler ascensionner
 ascétiser aseptiser asexuer asianiser asiatiser aspecter asphalter aspirer
 assabler assaisonner assassiner assembler assener asséner assermenter asserter
 assibiler assigner assimiler assister assoiffer assoler assommer assoner
 assoter assumer assurer asticoter astiquer athéiser atlantiser atomiser
 atourner atropiniser attabler attacher attaquer attarder attenter attentionner
 atténuer atterrer attester attifer attirer attiser attitrer attoucher attraper
 attremper attribuer attriquer attrister attrouper aubader aubiner
 audiovisualiser auditer auditionner augmenter augurer aulofer auloffer aumôner
 auner auréoler ausculter authentiquer autoaccuser autoadapter autoadministrer
 autoagglutiner autoalimenter autoallumer autoamputer autoanalyser autoancrer
 autoassembler autoassurer autocastrer autocélébrer autocensurer autocentrer
 autochtoniser autociter autoclaver autocoller autocomplimenter autocondenser
 autocongratuler autoconserver autoconsommer autocontester autocontrôler
 autocratiser autocritiquer autodéclarer autodénigrer autodénoncer autodésigner
 autodéterminer autodévelopper autodévorer autodicter autodiscipliner
 autodupliquer autoéduquer autoenchâsser autoenseigner autoépurer autoéquiper
 autoévaporiser autoévoluer autoféconder autofertiliser autoflageller
 autofonder autoformer autofretter autogouverner autogreffer autoguider
 auto-immuniser auto-ioniser autolégitimer autolimiter autoliquider autolyser
 automatiser automédiquer automitrailler automutiler autonomiser
 auto-optimaliser auto-optimiser autoorganiser autoperpétuer autopersuader
 autopiloter autopolliniser autoporter autopositionner autoproclamer
 autopropulser autoréaliser autorecruter autoréglementer autoréguler
 autorelaxer autoréparer autoriser autosélectionner autosevrer autostabiliser
 autostimuler autostopper autosubsister autosuggestionner autotomiser
 autotracter autotransformer autovacciner autoventiler avaler avaliser
 aventurer aveugler avillonner aviner avironner aviser avitailler aviver
 avoiner avoisiner avorter avouer axéniser axer axiomatiser azimuter azoter
 azurer babiller babouiner bâcher bachonner bachoter bâcler badauder bader
 badigeonner badiner baffer bafouer bafouiller bâfrer bagarrer bagoter bagouler
 baguenauder baguer baguetter bahuter baigner bailler bâiller baîller
 bâillonner baîllonner baiser baisoter baisouiller baisser bakéliser balader
 baladiner balafrer balancetiquer baleiner baliser baliver baliverner
 balkaniser balladuriser ballaster baller ballonner ballotter balourder
 balustrer bambocher banaliser bancariser bancher bander banderiller
 bandonéoner banner banquer baptiser baragouiner barander baraquer baratiner
 baratter barauder barbariser barber barbeyer barboter barbouiller barder
 barguigner barioler baroniser baronner baroquiser barouder barreauder barrer
 barricader barroter barytonner basaner basculer baser bassiner baster
 bastillonner bastinguer bastonner bastringuer batailler bâtarder batifoder
 batifoler batiker batiller bâtonner batourner baudouiner bauxitiser bavacher
 bavarder baver bavocher bavoter bayer bazarder bêcher bécoter bécotter becter
 bedonner beigner bêler béliner beloter belotter belouser bémoliser benchmarker
 benzoyler benzyler béquiller berdiner berginiser berlurer berner bertauder
 bertillonner bertouder besogner bessemeriser bestialiser bêtiser bétonner
 beugler beurrer biaiser bibarder bibeloter biberonner bicarbonater bicher
 bichonner bidistiller bidonner bidonvilliser bidouiller biduler biffer
 biffetonner biftonner bifurquer bigarrer bigler bigophoner bigorner bijouter
 biler bilinguiser billarder billebarrer billebauder biller billonner biloquer
 biner binoter biotraiter biotransformer biper bipolariser bipper birmaniser
 biscoter biscuiter biseauter biser bisiallitiser bismuther bisouter bisquer
 bissecter bisser bistourner bistrer bistrouiller biter bitter bitturer bitumer
 bituminer bituminiser biturer bivouaquer bizouter bizuter blablater
 blackbouler blaguer blaireauter blairer blaser blasonner blaster blesser
 bleuter blinder blinquer bloquer blouser bluetter bluffer bluter bobiner
 bocarder boësser boetter boffumer boguer boiser boissonner boitailler boiter
 boitiller boitter bolcheviser bolchéviser bolincher bombarder bomber bombiller
 bonder bondériser bondieuser bondonner bonimenter booster boquillonner borater
 bordéliser border bordurer boriquer borner borosilicater borurer boscarder
 bosser bosseyer bossuer bostonner botaniser botter bottiner boubouler boucaner
 boucharder boucher bouchonner boucler bouder boudiner bouffarder bouffer
 bouffonner bougonner bouiller bouillonner bouillotter bouler boulevarder
 bouleverser boulocher boulonner boulotter boultiner boumer bouquer bouquiner
 bourder bourdonner bourgeonner bourlinguer bourraquer bourrer bourriquer
 bourser boursicoter boursouffler boursoufler bousculer bouser bousiller
 boustifailler boutader bouter boutiquer boutonner bouturer bouziller bovaryser
 bowaliser boxer boyauter boycotter brachycéphaliser braconner brader brailler
 braiser braisiller bramer brancarder brancher brandiller brandonner
 brandouiller branler branlocher braquer braser brasiller brasseyer bravader
 braver bredouiller brelander bréler brêler breller brésiller bretailler
 brétailler bretauder bretter brichetonner bricoler brider briefer brifer
 brifetonner briffer briffetonner brifter briftonner brigander briguer
 brillanter brillantiner briller brimbaler brimballer brimer brinder
 bringuebaler bringueballer bringuer brinquebaler brinqueballer briocher
 brioler briquer briser britanniser brocanter brocarder brocher broder bromer
 bromurer broncher bronzer brosser brouetter brouillarder brouiller
 brouillonner broussailler brousser brouter bruiner bruisser bruiter brûler
 brumer brumiser bruncher brusquer brutaliser bruter bûcher bucoliser
 budgétiser buer buffériser buffler bugler bugner buiser buissonner bulgariser
 buller buquer bureaucratiser buriner buser busquer buter butiner butonner
 butter buvoter byzantiner byzantiniser cabaler cabaliser cabaner câbler
 cabosser caboter cabotiner cabrer cabrioler cacaber cacaoter cacarder cacher
 cachetonner cachotter cadastrer cadavériser cadeauter cadetter cadoter cadrer
 cafarder cafeter cafouiller cafter cageoler cagnarder cagner caguer cahoter
 caillebotter cailler caillouter cajoler calaminer calamistrer calamiter
 calancher calandrer calaouer calciner calculer calencher caler calfater
 calfeutrer calibrer californiser câliner caller calmer caloriser calotter
 calquer calter camarder cambrer cambrioler cameloter camer camionner camisoler
 camoufler camper camphrer canadianiser canaliser canarder cancaner canceller
 cancériser candidater candiser caner canneller canner cannibaliser canoniser
 canonner canoter canter cantiner cantonnaliser cantonner canuler caoutchouter
 caparaçonner caper capeyer capillariser capitaliser capitonner capituler
 caponner caporaliser capoter capser capsuler capter captiver capturer
 capuchonner caquer carabiner caracoler caracouler caractériser caramboler
 caraméliser carapater carbonater carboner carboniser carbonitrurer carbonyler
 carburer carcailler carder cardinaliser carer caresser carguer caricaturer
 carillonner carmer carminer carniser carotter caroubler carrer carrioler
 carrosser cartelliser cartonner cascader casemater caser caserner casquer
 castagner castillaniser castiller castrer cataboliser catalaniser cataloguer
 catalyser catapulter cataracter catastropher catcher catéchiser catégoriser
 cathétériser catholiciser catiner cauchemarder causaliser causer cautériser
 cautionner cavalcader cavaler caver caviarder ceintrer ceinturer cémenter
 cendrer censurer centraliser centrer centupler céphaliser céramiser cercler
 cerner césariser cesser cétoliser chabler chabroler chagriner chahuter chaîner
 chalouper chaluter chamailler chamarrer chambarder chambouler chambrer
 chamoiser champagniser champaniser champignonner champouigner champouiner
 chanfreiner chanfrer chanlatter chansonner chanter chantonner chantourner
 chaparder chapeauter chaperonner chapitrer chaponner chapoter chaptaliser
 charançonner charbonner charcuter chardonner chariboter charioter charivariser
 charlataner charmer charogner charpenter charquer charronner charruer
 charteriser châtaigner chatertonner chatonner chatouiller châtrer chauber
 chaucher chauder chauffer chauler chaumer chausser chavirer chélater chêmer
 cheminer chemiser chenailler chenaler chénevotter chènevotter chercher cherrer
 chevaler chevaucher cheviller chevretter chevronner chevroter chiader chialer
 chicaner chicorer chicoter chicotter chienner chiffonner chiffrer chigner
 chimiquer chimiser chimisorber chiner chinoiser chiper chipoter chiquenauder
 chiquer chirurgicaliser chlinguer chlorater chlorer chloritiser chloroformer
 chloroformiser chlorométhyler chlorovaporiser chlorurer chocolater chômer
 choper chopper choquer choser chouanner chouchouter choucrouter chougner
 chouler chouraver chourer chouriner christianiser chromaluminiser chromater
 chromatiser chromer chromiser chromolithographier chroniciser chroniquer
 chrysalider chuchoter chuinter chuter cibler cicatriser cicéroniser ciller
 cimenter cinématiser cingler cintrer circonvoisiner circuiter circulariser
 circuler cirer cisailler citer citronner civiliser clabauder claboter clairer
 claironner clamer clamper clampiner clampser clamser claper clapoter clapper
 clapser claquemurer claquer claquetter claudiquer claustrer clavarder
 claveliser claver clavetter clayonner cléricaliser clicher cligner clignoter
 climatiser clinquanter clinquer cliper cliquer clisser cliver clochardiser
 clocher clocter cloisonner cloîtrer cloner cloper clopiner cloquer clôturer
 clotûrer clouer clouter coaccuser coacerver coacher coadapter coagglutiner
 coaguler coaliser coaltarer coaltariser coanimer coarticuler cobelligérer
 cocaïniser cocarder cocheniller cocher côcher cochonner coconiser coconner
 cocooner cocoter coder codéterminer codiller coéditer coéduquer coexister
 coexploiter coexprimer coffiner coffrer cofonder cogiter cogner cogouverner
 cohabiter cohériter cohober coiffer coincher coincider coïncider coïter
 colchiciner collaber collaborer collationner collecter collectionner
 collectiviser coller collisionner colloquer colluvionner colmater
 colombianiser colombiner coloniser colorer coloriser colostomiser colporter
 colpotomiser coltiner columniser combiner combler commander commanditer
 commémorer commenter commercialiser comminer commissionner commotionner
 commuer communaliser communautariser communiquer communiser commuter
 compacifier compacter comparer compartimenter compenser compiler compisser
 complanter complémenter complétiviser complexer complimenter compliquer
 comploter comporter composer composter compoter compounder compresser
 comprimer comptabiliser compter compulser computer computériser concentrer
 conceptualiser concerner concerter concher conciliabuler concocter concomiter
 concorder concrétionner concrétiser concubiner condamner condenser condimenter
 conditionner confabuler confectionner confédéraliser confesser
 confessionnaliser configurer confiner confirmer confisquer confiter confluer
 conformer conforter confronter confusionner congestionner conglober
 conglutiner congoliser congratuler coniser conjecturer conjointer conjuger
 conjuguer conjurer connecter conniver connoter conquêter consacrer
 conscientiser conseiller conserver consigner consister consoler consolider
 consommariser consommer consonantiser consoner conspirer conspuer constater
 consteller conster consterner constiper constituer constitutionnaliser
 consulter consumer contacter contagionner containeriser containériser
 contaminer contemner contempler conteneuriser contenter conter contester
 contextualiser continentaliser contingenter continuer contorsionner contourner
 contracter contractualiser contracturer contraposer contraster contre-attaquer
 contrebouter contrebuter contrecalquer contrecarrer contre-expertiser
 contreficher contrefraser contre-indiquer contremander contremanifester
 contremarcher contremarquer contreminer contremurer contrenquêter
 contreplaquer contrepointer contrer contresigner contrespionner contretyper
 contreventer contribuer contrister contrôler controuver controverser
 contusionner conventionnaliser conventionner conventualiser converser
 convoiter convoler convoquer convulser convulsionner cooccuper coopératiser
 coopter coordonner coorganiser coparrainer coparticiper copermuter copiner
 copolycondenser copolymériser coprésenter coprésider copser copter copuler
 copyrighter coqueliner coquer coqueriquer coquiller corailler corder cordonner
 coréaliser coréaniser coréguler coresponsabiliser cornaquer cornemuser corner
 coroniser corporiser correctionaliser correctionnaliser correler corréler
 corroborer corroder corser corticaliser cosigner cosmétiquer cosser costumer
 coter cotillonner cotiser cotonner cotransfecter couaquer couarder couchailler
 coucher couchoter couchotter coucouer coucouler couder coudrer couillonner
 couiner couler coulisser coupailler coupeller couper couperoser coupler
 couponner courailler courbaturer courber courbetter courcailler couronner
 courrieler courser courtauder court-circuiter courtiser cousiner coussiner
 coûter couturer couver cracher crachiner crachoter crachouiller crailler
 cramer craminer cramper cramponner crampser cramser craner crâner crânoter
 cranter crapahuter crapaüter crapser crapuler craquer crasher cratériser
 craticuler cratoniser cravacher cravater crawler crayonner crédibiliser
 créditer crématiser créoliser créosoter crêper crépiner crépiter crésyler
 crêter crétiniser creuser criailler cribler criminaliser criquer crisper
 crisser cristalliser criticailler critiquer crocher croiser crôler croquer
 croskiller crosser crotoniser crotter crouler croupionner crouponner
 croustiller croûter croûtonner cryoappliquer cryocautériser cryocoaguler
 cryoconcentrer cryodécaper cryoébarber cryofixer cryogéniser cryomarquer
 cryosorber crypter cuber cueiller cuider cuisiner cuivrer culbuter culer
 culminer culotter culpabiliser cultiver culturaliser cumuler curariser
 curedenter curer curetter customiser cuter cutiniser cuver cyaniser cyanoser
 cyanurer cybernétiser cycler cycliser cycloner cylindrer dactylocoder daguer
 daguerréotyper daïer daigner dailler daller damasquiner damer damner
 damouritiser dandiner danser dansoter dansotter darder darsonvaliser dater
 dauber daufer dauffer daupher déactiver déafférenter déambuler déankyloser
 débâcher débâcler débagouler débaguer débâillonner débaleiner débaliser
 déballaster déballer déballonner débalourder débanaliser débander débanquer
 débaptiser débarasser débarbariser débarbouiller débarder débarquer débarrer
 débarricader débaucher débêcher débecquer débecqueter débecter débelgiciser
 débenzoler débenzoyler débétonner débeurrer débieller débiffer débiliser
 débiliter débillarder débiller débiner débiter débitumer débituminer déblinder
 débloquer débobiner déboguer déboiser déboîter débonder débondonner déborder
 débosser débotter déboucher déboucler débouder débouler déboulonner
 déboumediéniser débouquer débourber débourgeoiser débourrer débourser
 déboussoler débouter déboutonner débraguetter débrailler débraiser débrancher
 débraser débrider débriefer débringuer débriser débrocher débromer débronzer
 débrouiller débroussailler débrousser débrutaliser débruter débucher débûcher
 débudgétiser débuguer débuller débureaucratiser débusquer débutaniser débuter
 débutter décabosser décadrer décaféiner décaféiniser décaisser décalaminer
 décalcariser décaler décalfater décalotter décalquer décamper décanadianiser
 décanailler décaniller décanner décanoniser décanter décantonner
 décaoutchouter décaper décapitaliser décapiter décapitonner décapoter
 décapsuler décapuchonner décarbonater décarboniser décarbonyler décarboxyler
 décarburer décarêmer décarniser décarotter décarréliser décarrer décartelliser
 décartonner décaser décaserner décatégoriser décatholiciser décauser
 décavaillonner décaver décentraliser décentrer décercler décérébeller décerner
 décertifier décesser déchagriner déchaîner déchaler déchanter déchaper
 déchaperonner déchaptaliser décharançonner décharner déchatonner déchauler
 déchaumer déchausser décheminer déchevêtrer décheviller déchiffonner
 déchiffrer déchirer déchlorer déchlorurer déchoquer déchristianiser déchromer
 décibler décider déciller décimaliser décimer décintrer décirer déciviliser
 déclamer déclarer déclencher décléricaliser déclimater décliner déclinquer
 décliquer décliver déclocher décloisonner décloîtrer déclouer décoaguler
 décocaïniser décocher décoconner décoder décoeurer décoffrer décoiffer
 décollectiviser décoller décolmater décoloniser décolorer décombrer
 décommander décommuniser décompacter décompartimenter décompenser décomplexer
 décomplexifier décompliquer décomposer décompresser décomprimer décompter
 déconcentrer déconceptualiser déconcerter décondamner déconfessionnaliser
 déconforter décongestionner déconnecter déconner déconsacrer déconseiller
 déconsigner déconsolider déconstiper déconstitutionaliser
 déconstitutionnaliser décontaminer décontextualiser décontracter
 décontracturer décontrôler déconventionner décoquer décoquiller décorder
 décorer décorner décorréler décortiquer décoter décotter découcher découenner
 découler découper découpler décourber découronner décraber décranter
 décrapouiller décravater décrédibiliser décréditer décréer décrémenter
 décréoliser décrêper décrépiter décrétiniser décreuser décriminaliser
 décriquer décrisper décristalliser décrocher décroiser décrotter décroûter
 décruer décruser décrypter décuivrer déculotter déculpabiliser déculturer
 décupler décurariser décuscuter décuver décycliser dédaigner dédaller dédamer
 dédiviniser dédoler dédolomitiser dédorer dédosser dédotaliser dédouaner
 dédoubler dédramatiser dédroitiser déélectroner défâcher défaçonner défacturer
 défalquer défanatiser défaner défarder défarguer défasciser défatiguer
 défaufiler défauner défausser défavoriser défédéraliser déféminiser
 défenestrer déferler déferrailler déferrer déferriser défertiliser défeuiller
 défeutrer défibrer défibriller défibriner déficher défidéliser défigurer
 défiler défilialiser défilocher défiscaliser déflagrer déflaquer déflater
 déflegmer déflorer défluer défluorer défocaliser défolioter défonctionnaliser
 défonctionnariser déforester déformaliser déformater déformer défouetter
 défouler défourailler défourner défourrer défranchiser défranciser
 défranquiser défrapper défretter défricher défrimer défringuer défriper
 défriser défrisotter défroisser défroquer défruiter défubler défumer défuncter
 dégainer dégalonner déganter dégarer dégarouler dégasconner dégasoliner
 dégauchiser dégausser dégazer dégazoliner dégazonner dégêner dégermaniser
 dégermer dégingander dégîter dégivrer déglaçonner déglaiser déglinguer
 déglobaliser déglobuliser dégluer déglutiner déglycériner dégobiller dégoiser
 dégommer dégonder dégonfler dégoter dégotter dégoudronner dégouliner
 dégoupiller dégoûter dégoutter dégrabatiser dégrader dégrafer dégrainer
 dégraisser dégrammaticaliser dégranuler dégraphiter dégravillonner dégréciser
 dégrener dégréner dégriffer dégriller dégringoler dégripper dégriser dégrosser
 dégrouiller dégrouper dégueniller dégueuler déguiser dégurgiter déguster
 déhaler déhâler déhancher déharder déharnacher déhelléniser déhindouiser
 déhomériser déhotter déhouiller déhourder déhousser déidéologiser déioniser
 déjanter déjeuner déjeûner déjointer déjouer déjouter déjucher déjudaïser
 dékardeljiser dékoulakiser délabialiser délabrer délabyrinther délactoser
 délainer délaisser délaiter délaminer délarder délaver déléaturer délecter
 délégaliser délégitimer délenter délester déleucocyter délicoter délictualiser
 déligner déligoter délimiter délimoner délinéamenter délinéariser délinquer
 délirer délisser délister déliter délivrer délocaliser déloquer délourder
 délover délurer délustrer déluter démacadamiser démacler démaçonner
 démagnétiser démailler démaillonner démailloter démancher demander démandriner
 démaniller démanoquer démantibuler démaoïser démaquer démaquiller démarcher
 démargariner démarginer démarquer démarrer démarxiser démascler démasculiniser
 démasquer démasselotter démastiquer démater dématérialiser démathématiser
 dématriculer démécaniser démédicaliser démêler démembrer démensualiser
 démerder démériter démesurer démétalliser déméthaniser déméthyler démeubler
 demeurer démieller démilitariser déminer déminéraliser démissionner
 démobiliser démochristianiser démocratiser démoder démoduler démonétiser
 démoniser démonter démontrer démoraliser démorphiner démorphiniser démotiver
 démotoriser démouler démoustiquer démucilaginer démultiplexer démurer
 démutiser démyéliniser démysticiser démythologiser dénasaliser dénationaliser
 dénatter dénaturaliser dénaturer dénébuliser déniaiser dénicher dénicotiniser
 dénigrer dénitrater dénitrer dénoder dénombrer dénominer dénommer dénoter
 dénouer dénoyauter dentaliser denter dénucléariser dénuder dénuer déodorer
 déodoriser dépaganiser dépageoter dépaginer dépagnoter dépailler dépajoter
 dépalataliser dépaler dépalettiser dépalissader dépalisser dépanner
 dépanouiller dépapiller dépapilloter déparaffiner déparasiter déparcher
 dépareiller déparementer déparer déparfumer déparisianiser déparler
 départementaliser départiculariser dépassionner dépassiver dépastiller
 dépatouiller dépatter dépaver dépayser dépêcher dépécorer dépeigner
 dépeinturer dépeinturlurer dépelliculer dépelotonner dépénaliser dépenser
 dépentaniser dépersonnaliser dépersuader dépêtrer dépeupler déphaser
 déphlogistiquer déphonologiser déphosphater déphosphorer dépiauter dépierrer
 dépigeonniser dépigmenter dépiler dépingler dépiquer dépister dépistoliser
 dépiter déplafonner déplanquer déplanter déplaquetter déplastifier déplatiner
 déplâtrer déplisser déplomber déplorer déplumer dépocher dépoétiser dépoiler
 dépointer dépoitrailler dépolariser dépolitiser dépolluer dépoloniser
 dépolymériser dépontiller dépopulariser déporter déposer déposter dépoter
 dépoudrer dépouiller dépraver dépréparer dépresser dépressuriser déprêtriser
 déprimer dépriser dépriver déproblématiser déprogrammer déprolétariser
 dépropaniser déprovincialiser dépsychiatriser dépulper dépunaiser dépurer
 députer déqueusoter déquiller déraber déraciner dérader dérailler déraisonner
 déramer déraper dérâper déraser dérater dérationaliser dératiser déréaliser
 dérégionaliser déréglementer déréguler dérembourser déréprimer
 déresponsabiliser dérestaurer dérider dérigidifier dériver dérober dérocher
 dérocter déroder déroquer dérouiller dérouler dérouter déroyaliser dérueller
 déruraliser dérussiser désabonner désabouter désabriter désabuser désaccentuer
 désacclimater désaccorder désaccorer désaccoupler désaccoutumer désachalander
 désacraliser désactiver désadapter désadopter désaffecter désaffectionner
 désafférenter désaffleurer désaffourcher désaffubler désagater désagrafer
 désailer désaimanter désaimer désaisonnaliser désaisonner désajuster
 désalcoyler désaligner désaliniser désallouer désalper désalphabétiser
 désaluminiser désamarrer désambiguer désambiguïser désaméricaniser désamianter
 désamidonner désaminer désancrer désanctuariser désangler désangliciser
 désangoisser désankyloser désannexer désapeurer désappareiller désapparenter
 désappointer désapprouver désapprovisionner désarabiser désarchiver
 désarçonner désargenter désaristocratiser désarmer désarmorcer désaromatiser
 désarrimer désarticuler désasiatiser désasphalter désaspirer désassembler
 désassibiler désassimiler désassurer désatelliser désatomiser désattrister
 désaturer désauber désautoriser désaveugler désavouer désaxer désazoter
 desceller déschister déschlammer déscolariser désécailler déséchafauder
 déséchouer déséclairer désécologiser déséconomiser désectoriser
 déségrégationner désélectriser désémantiser désemballer désembarquer
 désembaucher désembobiner désembourber désembourgeoiser désembouteiller
 désembringuer désembrocher désembrouiller désembroussailler désembuer
 désemmancher désemmêler désemmieller désemmitoufler désemmurer désempailler
 désemparer désempêtrer désemphatiser désempierrer désempiler désemplumer
 désempoisonner désempoissonner désemprisonner désemprunter désémulsionner
 désenamourer désénamourer désencadrer désencanailler désencapsuler
 désencapuchonner désencarter désencartonner désencastrer désencaustiquer
 désenchaîner désenchanter désenchevêtrer désenclaver désenclencher désenclouer
 désencoller désencombrer désencorder désencroûter désencuivrer désendetter
 désendimancher désenfiler désenflammer désenfler désenfourner désenfumer
 désengazonner désenglober désengluer désengommer désenivrer désenliser
 désenrhumer désenrober désenrôler désenrouer désenrubanner désensabler
 désensacher désenseigner désenserrer désensibiliser désensommeiller
 désensoufrer désentartrer désenterrer désentêter désenthousiasmer désentoiler
 désentortiller désentraver désenturbanner désenvaser désenvenimer désenverguer
 désenvoûter désépargner désépauler désépingler déséquetter déséquilibrer
 déséquiper désergoter désérotiser déserter désertiser désétamer désétatiser
 déséthaniser désétoffer déseuropéaniser désexciter désexualiser déshabiliter
 déshabiller déshabiter déshabituer désharmoniser désharnacher désharponner
 déshémoglobiniser désherber déshériter désheurer déshistoriciser
 déshomogénéiser déshonorer déshospitaliser déshuiler déshumaniser déshydrater
 désiconiser désidéaliser désidentifier désidéologiser designer désigner
 désiler désilicater désillusionner désillustrer désimbriquer désimmuniser
 désimperméabiliser désincarner désincorporer désincruster désinculper
 désindemniser désindexer désindividualiser désindustrialiser désinfantiliser
 désinfatuer désinfecter désinféoder désinformatiser désinformer désinhiber
 désinitialiser désinsectiser désinstaller désintellectualiser désintéresser
 désinternationaliser désintoxiquer désintriquer désinvaginer désinventer
 désinviter désioniser désirer désislamiser désisoler désister désitalianiser
 désobstruer désobuser désoccidentaliser désocculter désoccuper désocialiser
 désodoriser désoeuvrer désofficialiser désoler désolidariser désolvater
 désongler désoperculer désophistiquer désopiler désorber désorbiter
 désordonner désorganiser désorientaliser désorienter désosser désoufrer
 désoutiller désoviétiser désoxyder déspécialiser déspiraliser déspiritualiser
 désponsoriser despotiser desquamer dessabler dessaigner dessaisonaliser
 dessaisonner dessaler dessaliniser dessangler dessaouler desseller desserrer
 dessiller dessiner dessoler dessoucher dessouder dessouler dessoûler
 dessuinter déstabiliser déstaliniser déstandardiser déstariser déstériliser
 destiner destituer déstocker déstresser destructurer déstructurer
 désubjectiviser désubstantialiser désubventionner désucrer désulfater
 désulfiter désulfurer désurbaniser désurchauffer désurtaxer désymboliser
 désynchroniser désyndicaliser détabler détabouiser détacher détailler détaler
 détalinguer détaller détalonner détalquer détamiser détanner détanniser
 détaper détapisser détarifer détartrer détatouer détaxer détayloriser
 détechnocratiser détecter détériorer déterminer déterminiser déterrer
 déterritorialiser détester déteutonner déthéâtraliser déthéiner déthésauriser
 détimbrer détiquer détirefonner détirer détisser détitiser détitrer détoner
 détonner détortiller détotaliser détourer détourner détoxiquer détracter
 détrancaner détrancher détrapper détraquer détremper détresser détribaliser
 détricoter détripler détromper détroncher détrôner détronquer détroquer
 détrousser détuber dévaginer dévaler dévaliser dévaloriser dévaluer dévaser
 dévaster développer déventer dévergonder déverguer déverrouiller déverser
 dévider deviner dévirer dévirginiser déviriliser déviroler deviser dévisser
 dévitaliser dévitaminer dévitaminiser dévocaliser dévoiler dévoiser dévoler
 dévolter dévorer dévouer dévriller dextriniser dézinguer diaboliser diaconiser
 diagnostiquer diagonaliser dialectaliser dialectiser dialoguer dialyser
 diamanter diapasonner diaphanéiser diaphaniser diaphragmer diaprer diastaser
 diazoter dichotomiser dicter diésélifier diéséliser diffamer diffluer
 difformer diffracter diffuser difluorer digitaliser digresser diguer
 dihydroxyler diioder dilapider dilater diligenter diluer dimensionner dîmer
 dimériser diminuer dindonner dîner dinguer dinitrer diogéniser diphtonguer
 diplexer diplomatiser diplômer dirimer discerner discipliner disconnecter
 discontinuer discorder discréditer discrétiser discriminer disculper
 discutailler discuter disjoncter disloquer dismuter disneyiser dispatcher
 dispenser disperser disponibiliser disposer disproportionner disputailler
 disputer disquer dissembler disséminer disserter dissimiler dissimuler
 dissiper dissoner dissuader distiller distinguer distribuer disubstituer
 divaguer diverticuler diviniser diviser divulguer dociliser documenter
 dodeliner dodiner dogmatiser doguer doigter dolenter doler dollariser
 dolomitiser domanialiser domestiquer dominer domotiser dompter donjuaniser
 donner doper dorer dorloter dormailler dormichonner dorsaliser doser dosser
 doter douaner doublecliquer double-cliquer doubler doublonner doucher douer
 douiller douter dracher drageonner dragonner draguer drainer draîner
 dramatiser draper draver dresdeniser dresser dribbler dribler driller driver
 droguer droitiser droper dropper drosser dualiser dudgeonner duiter dumper
 duper duplexer duplicater dupliquer duraminiser durer dynamiser dynamiter
 dysfonctionner ébarber ébaucher éberluer éberner éboguer éborgner ébosser
 ébotter ébouer ébouillanter ébouler ébourgeonner ébouriffer ébourrer ébouser
 ébousiner ébouter ébouturer ébraiser ébrancher ébranler ébraser ébrauder
 ébroder ébrouder ébrouer ébrousser ébruiter ébruter éburnifier écacher écaffer
 écailler écaler écanguer écapsuler écarbouiller écarder écarquiller écarter
 écarver ecchymoser écepper échafauder échaloter échancrer échantillonner
 échanvrer échapper échardonner écharner écharper écharpiller échauder
 échauffer échauler échaumer échelonner écheniller échevetter échigner échiner
 écholocaliser échopper échosonder échouer écimer éclabousser éclairer éclater
 éclipser éclisser écloper écluser écobuer écoeurer écoiner écointer écologiser
 économiser écoper écorcher écorer écorner écornifler écosser écôter écouler
 écourter écouter écrabouiller écraminer écraser écrêter écrivailler écroter
 écrouer écrouler écroûter ectomiser écuisser éculer écumer écurer écussonner
 eczématiser édéniser édenter édicter éditer éditorialiser édulcorer éduquer
 éfaufiler effaner effarer effaroucher effectuer efféminer effeuiller effiler
 effilocher effiloquer efflanquer effleurer efflorer effluer effluver effondrer
 effriter effruiter effumer effuser égailler égaler égaliser égarer égauler
 églomiser égobler égorgiller égosiller égousser égoutter égrainer égraminer
 égrapper égratigner égravillonner égriser égueuler égyptianiser éherber
 éhouper éjaculer éjarrer éjecter éjointer élaborer élaguer élaïdiser élaiter
 élaver électriser électrocuter électrodéposer électrolocaliser électrolyser
 électroner électroniser électropolymériser électropuncturer électrozinguer
 élégantiser éliciter élider élimer éliminer élinguer ellipser éloigner
 élucider élucubrer éluder éluer émailler émanciper émaner émasculer
 embabouiner emballer emballotter embaluchonner embalustrer embander
 embarbouiller embarder embarquer embarrer embastiller embastionner embâtonner
 embaucher embaumer embecquer embéguiner emberlicoquer emberlificoter
 emberloquer emberlucoquer embesogner embêter embidonner embieller emblaver
 emblématiser embler embobeliner embobiner emboiser emboîter emboliser embosser
 emboucaner emboucauter emboucher emboucler embouer embouquer embourber
 embourgeoiser embourrer embourser embouser embouteiller embouter embrancher
 embraquer embraser embrelicoquer embreuver embrigader embringuer embrocher
 embrouiller embroussailler embruiner embrumer embûcher embuer embusquer
 émender émerillonner émeriser émerveiller émétiser émeuler émietter émigrer
 emmagasiner emmailler emmailloter emmancher emmarquiser emmêler emmenotter
 emmerder emmeuler emmiasmer emmieller emmitonner emmitouffler emmitoufler
 emmotter emmoufler emmouscailler emmurailler emmurer émonder émorfiler
 émotionner émotter émoucher émousser émoustiller empaffer empailler empaler
 empalmer empanacher empanner empapaouter empapillonner empapilloter
 emparadiser emparer emparquer empatter empaumer empêcher empeigner empeloter
 empelotonner empenner emperler emperruquer empester empêtrer emphatiser
 empierrer empiffrer empiler empirer emplanter emplastrer emplâtrer emplomber
 emplumer empocher empoicrer empoigner empointer empoisonner empoisser
 empoissonner empommer emporter empoter empourprer empouter empresser
 emprésurer emprisonner emprunter émuler émulsionner enamourer énamourer
 enarbrer énaser encabaner encadrer encagouler encaisser encalminer encanailler
 encaper encapsuler encapuchonner encaquer encarter encartonner encaserner
 encaster encastrer encaustiquer encaver enceinter enceintrer encenser
 encéphaliser encercler enchaîner enchanter enchaper enchaperonner encharbonner
 encharner enchasser enchâsser enchatonner enchausser enchaussumer enchemiser
 enchevaler enchevaucher enchevêtrer encirer enclaver enclencher encloîtrer
 enclouer encocher encoder encoffrer encoigner encoller encombrer encorbeller
 encorder encorner encoubler encourtiner encrer encrister encroiser encrotter
 encrouer encroûter encrypter encuivrer enculer encuver endauber endenter
 endetter endeuiller endêver endiabler endiamanter endiguer endimancher
 endisquer endivisionner endoctriner endogénéiser endosmoser endosser
 endothélialiser endouzainer endrailler endurer énergétiser énergiser énerver
 éneyer enfaçonner enfaîter enfanter enfariner enfermer enferrailler enferrer
 enficher enfieller enfiler enflammer enflaquer enfler enfleurer enformer
 enfosser enfourcher enfourner enfricher enfumer enfutailler enfûter engainer
 engaller engamer enganter engargousser engaver engazonner engeigner engendrer
 engerber englaçonner englober engluer engober engommer engouer engouffrer
 engouler engraisser engraver engrêler engrisailler engrosser engueuler
 engueuser enguicher enguirlander enharnacher enherber énieller enivrer enjaler
 enjamber enjanter enjôler enjoliver enjouer enjouguer enjuguer enjuiver
 enkikiner enkyster enlarmer enligner enlinceuler enliser enluminer énoliser
 énoper énouer enquêter enquiller enquinauder enquiquiner enraciner enrailler
 enrégimenter enregistrer enrêner enrésiner enrhumer enrober enrocher enrôler
 enrouer enrouiller enrouler enrubanner ensabler ensaboter ensacher ensafraner
 ensaisiner ensanglanter ensauver enseigner enseller enserrer enseuiller
 ensiler ensiloter ensimer ensoleiller ensommeiller ensoufrer ensouiller
 ensoupler ensoutaner ensucrer ensuifer ensuquer entabler entacher entâcher
 entailler entamer entaquer entartrer enter entériner enterrer entêter
 enthousiasmer enticher entoiler entôler entomber entonner entortiller entourer
 entourlouper entraccorder entraccuser entradmirer entraider entraîner entraver
 entrebailler entrebâiller entrechoquer entreciter entrecouper entrecroiser
 entredéchirer entre-déchirer entredévorer entre-dévorer entredonner
 entrefermer entregloser entregreffer entrelarder entrelouer entremêler
 entrepardonner entrepointiller entreposer entrequereller entrer entreregarder
 entreserrer entretailler entreteiller entretoiser entretuer entrevoûter
 entrexaminer entruster entuber enturbanner énupler énuquer envacuoler envaler
 envaper envaser envelopper envenimer enverguer enverrer envider envirer
 environner envoiler envoisiner envoler envoûter enwagonner éoliser épailler
 épaler épamprer épancher épanner épanouiller épargner éparpiller épater
 épaufrer épauler épépiner éperonner épeuler épeurer épierrer épigéniser
 épilamer épiler épiloguer épimériser épiner épingler épisser épithélialiser
 épithétiser éplorer éplucher époiler époinçonner épointer épointiller
 épontiller épouffer épouiller époumoner époumonner épouser époustoufler
 épouvanter éprouver épuiser épurer équerrer équeuter équilibrer équiper
 équipoller équivoquer éradiquer érafler érailler éreinter ergoter éroder
 érotiser errer éructer érusser esbigner esbroufer esbrouffer escadronner
 escalader escaler escaloper escamoter escamper escaper escarbiller
 escarbouiller escarmoucher escarper escher esclaffer esclavagiser escobarder
 escompter escorter escrimer escroquer esgourder esmiller espagnoliser espalmer
 espionner espoliner espouliner esquicher esquimauter esquinter esquisser
 esquiver essaimer essarder essarmenter essarter esseimer essemiller
 essentialiser esseuler essimer essimpler essorer essoriller essoucher
 essouffler essoufler estafilader estamper estampiller ester esthétiser estimer
 estiver estocader estomaquer estomper estoquer estrapader estroper établer
 étaler étalinguer étalonner étamer étamper étancher étançonner étarquer
 étatiser étaupiner éterniser éternuer étêter éthériser ethniciser éthyler
 étioler étirer étoffer étoiler étonner étouffer étouper étoupiller
 étrangéifier étranger étrangler étraper étremper étrenner étrésillonner
 étriller étriper étriquer étriver étrogner étronçonner étuver étymologiser
 euphémiser euphoriser européaniser européiser eutrophiser évacuer évader
 évaginer évaguer évaltonner évaluer évangéliser évaporer évaser éveiller
 éveiner éventer éventiller éventrer éverdumer éverser évertuer évider éviter
 évoluer évoquer exacerber exalter examiner exarcerber excardiner excaver
 exceller excentrer excepter exciper exciser exciter exclamer excrémenter
 excursionner excuser exécuter exempter exfiltrer exhaler exhalter exhausser
 exhiber exhorter exhumer exiler existantialiser existentialiser exister
 exonder exorbiter exorciser exostoser exotiser expanser expansionner
 expectorer expérimenter expertiser expirer explanter expliciter expliquer
 exploiter explorer exploser exponctuer exporter exposer exprimer expulser
 exsuder exsuffler exténuer extérioriser exterminer externaliser extirper
 extorquer extrader extradosser extrapéritoniser extrapoler extraposer
 extraterritorialiser extravaguer extravaser extrémiser extrêmiser exulter
 fabricoter fabriquer fabuler façadiser facetter fâcher faciliter façonner
 factionner factoriser facturer fader fagoter failler fainéanter faisander
 falquer faluner familiariser fanatiser faner fanfaronner fanfrelucher
 fantasmer faonner faradiser farandoler farauder farder farfouiller farguer
 fariboler fariner farnienter farter fasciner fasciser faseyer faséyer fatiguer
 fauberder fauberter faucarder faucher fauciller fauder faufiler fausser fauter
 favéliser favoriser faxer fayoter fayotter fébriliser féconder féculer
 fédéraliser féeriser féériser feinter fêler féliciter fellationner féminiser
 fendiller fenestrer fenêtrer fénitiser féodaliser ferler fermenter fermer
 ferrailler ferralitiser ferrer ferrouter ferruginer ferruginiser fertiliser
 fesser festonner fêter fétichiser feuiller feuilletiser feuilletoniser
 feuilletonner feuilloler feuillurer feuler feutrer fiabiliser fibrer fibriller
 fibuler ficher fidéliser fieffer fienter fifrer fignoler figurer filer
 filialiser filiforer filigraner filleriser fillonner filmer filocher
 filoguider filouter filtrer finaliser financiariser finlandiser fionner
 fioriturer fiscaliser fissionner fissurer fistuliser fitter fixer flacher
 flageller flageoler flagorner flairer flamandiser flamber flammer flancher
 flâner flânocher flânoter flanquer flaquer flasher flâtrer flatter flegmatiser
 flemmarder flemmer fletter fleurdeliser fleurer fleuronner flexibiliser
 flibuster flinguer flinquer flipper fliquer flirter floconner floculer floquer
 florer flotter flouer fluater fluber fluctuer fluer fluidiser fluorer
 fluoriser fluorurer flûter flytoxer focaliser foccardiser foéner foëner
 foetaliser foirer foisonner folâtrer foliariser folichonner folioter
 folkloriser fomenter fonctionnaliser fonctionnariser fonctionner fonder
 fordiser forer forfaitariser forfaitiser forhuer forligner formaliser formater
 former formoler formuer formuler formyler forniquer forpaiser forwarder
 fossiliser fouailler fouetter fouiller fouiner foularder fouler foulonner
 fourailler fourber fourcher fourgonner fourguer fourmiller fourrer fractionner
 fracturer fragiliser fragmenter fraiser framboiser franchiser franciser
 franfrelucher frankliniser fransquillonner frapper fraterniser frauder
 fredonner frégater freiner frelater fréquenter frétiller fretter fricoter
 frictionner frigéliser friller frimater frimer fringaler fringuer friper
 friponner friseliser friser frisoter frisotter frissonner fritter froisser
 frôler fronder froquer frotailler frotter frouer froufrouter fructidoriser
 fruiter frusquer frustrer fuguer fulgurer fulminer fumailler fumer fumeronner
 fumoter funester funkifier furibonder fuser fusiller fusiner fusionner
 futiliser gaber gabionner gâcher gadgétiser gafer gaffer gagner gainer
 galantiser galber galer galipoter galler galocher galonner galoper galopiner
 galvaniser galvanocautériser galvauder gamahucher gambader gambergeailler
 gambeyer gambiller gaminer gangréner gangstériser ganser ganter garçonner
 garder gardienner garer gargariser gargoter gargouiller garrotter gasconner
 gaspiller gastrectomiser gastrotomiser gaucher gauchiser gaufrer gauler
 gauloiser gausser gaver gazer gazonner gazouiller gégèner géhenner gélatiner
 gélatiniser géliver gemeller gémeller géminer gemmer gendarmer gendarmiser
 gêner généraliser génoper géométriser gerber germaniser germer germiner
 gesticuler ghettoïser giberner gibouler gicler gifler gigoter giguer ginginer
 ginguer girer gironner girouetter gîter givrer glacielliser glacifier glairer
 glaiser glander glandouiller glaner glavioter glaviotter glisser globaliser
 globuliser gloser glottaliser glottorer glouglouter glousser gloutonner gluer
 glycériner gobeloter gober gobichonner godailler gödeliser gödéliser goder
 godiller godronner goguenarder goinfrer golfer goménoler gominer gommer gonder
 gondoler gonfler gorgeonner gouacher gouailler goualer gouaper goudronner
 goujonner goupiller goupillonner gourbiller gourer gourmander gourmer
 gournabler goûter goutter gouverner grabatiser grâcier gracieuser graciliser
 grader graduer graffigner graffiter grafigner grailler graillonner grainer
 graisser grammaticaliser grangrener graniter granitiser granuler graphiquer
 graphiter graphitiser grappiller grappiner grasseyer graticuler gratiner
 gratouiller gratter grattouiller graver gravillonner graviter gravurer
 gréciser grecquer grediner greffer grégariser grêler grelotter grenader
 grenailler grenouiller grenter grésiller grésillonner greviller gribouiller
 griffer griffonner grigner grignoter griller grimer grimper grincher
 gringotter gringuer gripper grisailler griser grisoler grisoller grisonner
 grivoiser grogner grognonner gronder grouiller grouiner grouper
 groupusculariser gruauter gruer grusiner gruter guêper guerdonner guêtrer
 guetter gueuler gueuletonner gueusailler gueuser guider guidonner guigner
 guignoler guiller guillocher guillotiner guimper guincher guinder guiper
 guirlander guitariser guniter gutturaliser gypser gyrer habiliter habiller
 habiter habituer habler hâbler hacher hachurer haleiner haler hâler halluciner
 halogéniser halter hameçonner hancher handicaper hanner hannetonner hanter
 happer haranguer harder harmoniser harnacher harnaquer harpailler harper
 harpigner harponner hasarder haubaner hausser haver hébraïser hégémoniser
 héliporter hélitreuiller helléniser hématoser hémiacétaliser hémidécérébeller
 hémisacraliser hémisphérectomiser hémodialyser hémolyser hépatectomiser
 hépatiser herbeiller herber herboriser hercher hérisser hérissonner hériter
 héroïser herscher herser hésiter hétéro-immuniser heurter hiberner hiberniser
 hier hiérarchiser hindouiser hispaniser hisser historialiser historiciser
 historiser histrionner hivériser hiverner hocher hogner hôler hominiser
 homogénéiser homologuer homopolymériser homosexualiser hongrer honorer
 horizonner horizontaliser hormoner horodater horripiler hospitaliser hotter
 houblonner houer houler houpper hourailler hourder houspiller housser
 houssiner hucher huer huiler hululer humaniser humecter humer hurler
 hurtebiller hussarder hutter hybrider hydrater hydrocraquer hydrocuter
 hydrodésalkyler hydrodésulfurer hydroformer hydrolyser hydrophiliser
 hydroplaner hydropneumatiser hydroraffiner hydroxyler hygiéniser hyperboliser
 hypercapitaliser hypercentraliser hypercoder hyperdilater hyperhumaniser
 hypermédiatiser hypermilitariser hypermonétariser hyperorganiser
 hyperplanifier hyperpolariser hyperqualifier hyperrationaliser
 hypersélectionner hypersensibiliser hyperspécialiser hyperstratifier
 hypnotiser hypotéquer hystériser iconiser idéaliser idéologiser idiotiser
 idolâtrer ignorer illettrer illimiter illuminer illusionner illustrer illuter
 imaginer imbiber imbriquer imiter immatérialiser immatriculer immigrer imminer
 immobiliser immoler immortaliser immuniser impacter impaluder impatienter
 impatroniser imperméabiliser impersonnaliser impétiginiser implanter
 implémenter impliquer implorer imploser importer importuner imposer impréciser
 impressionner imprimer improuver improviser impulser imputer inactiver inalper
 inaniser inaugurer incaguer incardiner incarner incidenter inciser inciter
 incliner incomber incommoder incorporer incrémenter incriminer incruster
 incuber inculper inculquer incurver indaguer indéfiniser indemniser indenter
 indéterminer indexer indianiser indigéniser indigestionner indigner indiquer
 indisposer individualiser individuer indoloriser indonésianiser indurer
 industrialiser inégaliser infantiliser infatuer infecter inféoder inférioriser
 infester infibuler infiltrer infirmer influer informatiser informer
 infroissabiliser infuser ingurgiter inhaler inhiber inhumer initialer
 initialiser injecter innerver innocenter innover inoculer inonder inquarter
 insaliver insculper insécuriser inséminer insensibiliser insinuer insister
 insoler insolubiliser insonoriser inspecter inspirer instabiliser installer
 instantanéiser instaurer instiguer instiller instituer institutionnaliser
 instrumentaliser instrumenter insuffler insulariser insulter insupporter
 intailler intellectualiser intenter intentionnaliser intentionner interboliser
 intercaler intercepter interconnecter intéresser interféconder intérioriser
 interjecter interligner interloquer internaliser internationaliser interner
 internétiser interpeller interpoler interpolliniser interposer interrelier
 intersecter intersectionner interviewer intimer intimider intituler intoxiquer
 intrigailler intriguer intriquer introjecter introniser intuber intuiter
 intuitionner inutiliser invaginer invalider invectiver inventer inverser
 investiguer inviter involuer invoquer ioder iodler iodurer ioniser iouler
 irakiser iraniser iriser irlandiser ironiser irréaliser irriguer irriter
 irruer islamiser islandiser iso-immuniser isoler isomériser israéliser
 italianiser italiser ivoiriser ivrogner jabler jaboter jacter jaffer jalonner
 jalouser jamber jambonner japonaiser japoniser japonner japper jardiner
 jargauder jargonner jaroviser jaser jasper jaspiner javaniser javelliser
 jazzer jérémiader jerker jésuiter jésuitiser jeûner jobarder jodler jogger
 joggliner jointer joncher jongler jordaniser jouailler joualiser jouer
 journaliser jouter jouxter jubiler jucher judaïser judiciariser juguler
 jumboïser jumper juponner jurer juridiciser juridictionnaliser juridiser juter
 juxtaposer kaoliniser kératiniser khomeiniser kidnapper kiffer klaxonner
 knockouter knouter krarupiser labéliser labelliser labialiser labourer lâcher
 lactoniser lactoser ladiniser laguner laïciser lainer laisser laitonner
 laïusser lambiner lambrequiner lambrisser lameller lamenter lamer laminer
 lamper lancequiner lanciner languetter langueyer lansquiner lanter lanterner
 lantiponer lantiponner laper lapider lapiner lapiniser laquer larder lardonner
 larguer larmer larronner larver laryngectomiser laseriser latéraliser
 latériser latéritiser latiniser latter laudaniser laurer laver lavougner
 léchonner léchotter légaliser légender légitimer légitimiser lemmatiser lenter
 lépariniser lésiner lessiver lester lettrer leurrer léviter levrauder
 levretter levurer lexicaliser lézarder liaisonner liarder libaniser libeller
 libéraliser libertiner lichéniser licher liciter lifter ligaturer ligner
 ligoter liguer liker limaçonner limander limer limiter limoner limousiner
 linéamenter linéariser lingoter linguer linotyper liquider liser liserer
 lisérer lisser lister liteauner liter lithochromiser litonner litrer
 littérariser littératurer livrer lober lobotomiser localiser locher lockouter
 lofer loffer lombaliser loquer lorgner lotionner loubardiser loucher louer
 louper lourder lourer louver lover lucher luncher luner lunetter lustrer
 lutéiniser luter lutiner lutter luxer lyncher lyophiliser lyrer lyriser lyser
 macadamiser macdonaldiser mâcher mâchiller machiner mâchonner mâchoter
 mâchouiller mâchurer macler maçonner macquer maculer madériser madraguer
 madrigaliser maffioter magasiner magner magnétiser magnétoscoper magouiller
 magyariser mailer mailler maillonner maîtriser majorer makhzéniser
 malaisianiser malaxer malléabiliser malléiner malter maltraiter malverser
 manchonner mandater mander mandriner mangeailler mangeotter manifester
 manipuler mannequiner manoeuvrer manoquer manquer mansarder manualiser
 manucurer manufacturer manufacturiser manutentionner maquer maquereauter
 maquereller maquignonner maquiller marauder marbrer marchandailler marchander
 marchandiser marcher marcotter margauder marginaliser marginer margoter
 margotter mariner marivauder marmiter marmonner marmoriser marmotter marner
 marocaniser maronner maroquiner marotiser maroufler marquer marrer marronner
 marsouiner marsupialiser martiner martingaler martingaliser martyriser
 marxiser masculiniser masquer massacrer masselotter massicoter mastériser
 mastiquer masturber matcher mater mâter matérialiser maternaliser materner
 materniser mathématiser mâtiner matraquer matriculer matter maturer
 mauritaniser maximaliser maximer maximiser mazer mazouter mazurker mécaniser
 mécompter mécontenter médailler médeciner médiatiser médicaliser médicamenter
 médiser méditer méduser mégisser mégoter mélancoliser mélaniser mêler
 méliniter mélodramatiser membrer mémoriser mendigoter menotter mensualiser
 mensurer mentaliser mentholer mentionner menuiser méphitiser mépriser
 mercantiliser merceriser mercurer merder meringuer mériter merliner merlonner
 mésarriver mésestimer mésinformer mesmériser mesurer mésuser métaboliser
 métalliser métamériser métamictiser métamorphiser métamorphoser métaphoriser
 métempsychoser météoriser méthaniser méthyler métisser métriser meubler
 meugler meuler meuliériser mexicaniser miauler michetonner microdoser
 microficher microfilmer micromanipuler microminiaturiser microniser
 microplisser microprogrammer microsabler microsouder microter mignoter
 migrainer migrer mijoter mildiouser militariser militer millerander millésimer
 mimer mimétiser minauder miner minéraliser miniaturer miniaturiser minimaliser
 minimiser miniteliser minorer minoriser minotauriser minuter miraculer
 mirailler mirer miroiter miser missionner mitadiner miter mithridater
 mithridatiser mitonner mitrailler mixer mixter mixtionner mobiliser modaliser
 modéliser modérantiser moderniser moduler moellonner mofler moirer moiser
 moissonner molarder molariser moléculariser molester moletter mollarder
 molletonner molletter monarchiser mondaniser monder mondialiser monétariser
 monétiser moniliser monologuer monomériser monophtonguer monopoler monopoliser
 monoprogrammer monosiallitiser monotoniser monseigneuriser monter montrer
 monumentaliser moquer moquetter morailler moraliser mordailler mordiller
 mordillonner mordorer mordoriser morfailler morfaler morfiler morfler morganer
 morguer morner morphologiser morplaner mortaiser mosaïquer motionner motiver
 motoriser motter moucharder moucher moucheronner moufeter mouffer mouffeter
 moufler moufter mouiller mouler mouliner moulurer mouronner mousseliner
 mousser moutarder moutonner mouvementer mouver moyenner moyetter mucher muer
 muloter multilatéraliser multimédiatiser multinationaliser multipler
 multiplexer multipolariser multiprogrammer municipaliser munitionner murailler
 murer murmurer musarder muscler muséaliser muser musiquer musquer musser muter
 mutiler mutiner mutualiser myéliniser myloniser mylonitiser myorelaxer
 myristiquer myrrher mysticiser nacrer namibianiser naniser napalmer napalmiser
 naphtaliner napper napperonner narcoser narcotiser narguer narrativiser narrer
 nasaliser nasarder nasillarder nasiller nasillonner nationaliser natter
 naturaliser navaliser navigabiliser naviguer navrer néantiser nébuliser
 nécessiter nécroser négativer négativiser néoformer néolithiser néologiser
 néosynthétiser néphrectomiser néphrostomiser néphrotomiser nerver nervurer
 neuraliser neuroleptiser neurotiser neutraliser neutrodyner névroser niaiser
 nicher nicotiniser nicotiser nider nieller nigauder nimber nipper niquer
 nitrater nitrer nitroser nitrurer nobeliser nobéliser noctambuler noliser
 nomadiser nombrer nominaliser nominer nommer nonupler noper nopper nordester
 nordouester normaliser normander normandiser normer notabiliser noter nouer
 novelliser nover noyauter nucléariser nuer nuiter numériser numéroter nupler
 nymphoser objecter objectiver objurguer obliquer obnubiler obombrer observer
 obstiner obstruer obturer occasionner occidentaliser occulter occuper
 océaniser ocrer octupler odorer odoriser oedématiser oedipianiser oeillader
 oeilletonner oeuvrer offenser officer officialiser offusquer oligomériser
 oligopoliser olinder olofer oloffer omaniser ombiliquer ombrer onder onduler
 opaliser operculer opiner opiniâtrer opposer oppresser opprimer opsoniser
 opter optimaliser optimiser oraliser orbiter orchestrer ordonner organiciser
 organiser organsiner orientaliser orienter originer ornementer orner
 orthogonaliser orthonormaliser oscariser osciller osculter oser ossianiser
 ostraciser ôter ouater ouatiner ouiller ouralitiser ourler outer outiller
 outrecuider outrer ouvrer ouvriériser ovaliser ovariectomiser ovationner
 ovuler oxycouper oxyder oxytoniser ozoner ozoniser packer pacotiller pacquer
 pacser pactiser paddocker padouer paganiser pageoter paginer pagnoter
 paillarder paillassonner pailler paillonner paissonner pajoter pakistaniser
 palabrer paladiner palancrer palangrer palanquer palataliser palatiser
 paletter palettiser palissader palisser palissonner palmer paloter palper
 palpiter palucher panacher panader pancarter paner paniquer panneauter panner
 pannetonner panoramiquer panser pantiner pantomimer pantoufler paoner paonner
 papelarder papillonner papilloter papoter papouiller paquer paraboliser
 parachuter parader parafer paraffiner paraisonner paralléliser paralyser
 paramétriser parangonner parapher paraphraser parasiter parcellariser
 parceller parcelliser parcheminer parcoriser pardonner parementer
 parenthétiser parer paresser parfiler parfumer parisianiser parjurer
 parkériser parlementer parler parloter parlotter parquer parrainer participer
 particulariser partitionner partouzer pasquiner pasquiniser passefiler
 passementer passepoiler passeriller passionnaliser passionner pasteller
 pasteuriser pasticher pastiller pastoriser patafioler pateliner patenter
 paternaliser paterner pathétiser patienter patiner pâtisser patoiser pâtonner
 patouiller patrimonialiser patrociner patronner patrouiller patter pâturer
 paumer paupériser pauser pavaner paver pavoiser peaufiner pébriner pécher
 pêcher pécloter pectiser pédaler pédanter pédantiser pédiculiser pédicurer
 pédimenter peigner peiner peinturer peinturlurer péjorer pelaner pelauder
 péleriner pèleriner pelletiser pelleverser pelliculer peloter pelotonner
 pelucher pelurer pénaliser pencher pendeloquer pendiller pendouiller penduler
 pénéplaner penser pensionner peptiser peptoniser percaliner percher percoler
 percuter perdurer pérégriner pérenniser perfectionner perforer performer
 perfuser péricliter périmer périodiser périphériser périphraser péritoniser
 perler permanenter permaner perméabiliser permuter pérorer pérouaniser
 peroxyder perpétuer perquisitionner perreyer perruquer persécuter persifler
 persiller persister personnaliser persuader perturber pervibrer pester
 pétarader pétarder pétiller pétitionner pétocher pétouiller pétrarquiser
 pétroliser pétuner peupler pexer phacoémulsifier phagocyter phalangiser
 pharyngaliser phéniquer phénoler phényler philosophailler philosopher
 phlébotomiser phlegmatiser phlogistiquer phonétiser phonologiser phosphater
 phosphorer phosphoriser phosphoryler photoactiver photocomposer photograver
 photo-ioniser photoïoniser photomonter photophosphoryler photopolymériser
 photosensibiliser phraser piaffer piailler pianomiser pianoter piauler pickler
 picocher picoler picorer picoter picouser picouzer picrater pictonner
 picturaliser pidginiser piédestaliser pierrer piétiner piétonnifier
 piétonniser pieuter pifer piffer piffrer pigeonner pigmenter pigner pignocher
 pignoler piler piller pilloter pilonner piloter pimenter pinailler pinceauter
 pinçoter pindariser pinter piocher pionner piotter piper piqueniquer
 pique-niquer piquer piquetonner piquouser piquouzer pirater pirouetter piser
 pisser pissoter pissouiller pistacher pister pistoler pistonner pitancher
 pitcher piter pitonner pituiter pivoter placarder placardiser plafonner
 plaider plainer plaisanter plamer plancher planer planétariser planétiser
 planquer planter plaquer plasmolyser plastiquer plastronner platiner
 platiniser platoniser plâtrer plébisciter pleurailler pleuraliser pleurer
 pleurnicher pleuroter pleuviner pleuvioter pleuvoter plisser plissoter plomber
 ploquer plotiniser plouter ploutrer plucher plumarder plumer pluraliser
 plussoyer pluviner pluvioter pocharder pocher pochetronner pochtronner poculer
 podzoliser poêler poétiser poignarder poigner poiler poinçonner pointer
 pointiller poireauter poirer poiroter poisser poitriner poivrer poivroter
 polariser poldériser polémiquer polissonner politicailler politiquer politiser
 polker polliciser polliniser polluer poloniser polychromer polycontaminer
 polygoner polygoniser polymériser polyploïdiser polytransfuser polyviser
 pommader pommer pomper pomponner ponctionner ponctuer ponter pontiller
 populariser poquer porer porphyriser porter porteuser portionner
 portoricaniser portraicturer portraiturer poser positionner positiver
 possibiliser postdater poster postérioriser posticher postillonner postposer
 postsonoriser postsynchroniser postuler potabiliser potentialiser poter
 poteyer potiner poudrer pouffer pouiller pouliner pouloper poulotter pouponner
 pourpenser pourprer poussailler pousser poutser praliner pratiquer
 préaccentuer préadapter préallouer préassembler préassimiler préaviser
 précariser précautionner prêchailler préchauffer préchauler prêcher précipiter
 préciser préciter précompter préconditionner préconfigurer préconiser
 préconstituer précoter prédater prédécouper prédésigner prédestiner
 prédéterminer prédiffuser prédilectionner prédiquer prédisposer prédominer
 préemballer préempter préencoller préenregistrer préenrober préexaminer
 préexister préfabriquer préfaner préfigurer préfixer préformater préformer
 préformuler préfritter préimprimer préinstaller prélaquer prélaver préliber
 préluder prémagnétiser prémédiquer préméditer prémonter prénommer préoccuper
 préopiner préordonner préorganiser préozoner préparer préposer prépositionner
 préprogrammer préscolariser présélectionner présensibiliser présenter
 préserver présidentialiser présider présignaliser présonoriser presser
 pressurer pressuriser préstructurer présumer présupposer présurer prétailler
 prétanner prêter prétester prétexter prétintailler prévariquer préverber
 primariser primer primherber printaniser prioriser priser prismatiser prismer
 privatiser priver probabiliser problématiser processionner procès-verbaliser
 proclamer procrastiner procurer prodiguer proéminer profaner professer
 professionnaliser profiler profiter programmer progresser prohiber
 prolétariser promotionner promulguer prôner pronominaliser pronostiquer
 prophétiser propoliser proportionner proposer propulser propylitiser prosaïser
 prospecter prosterner prostituer prostrer protéiner protéolyser protestaniser
 protestantiser protester protoner prototyper protracter prouter prouver
 provençaliser proverbialiser provigner provincialiser provisionner provoquer
 prussianiser pschuter psychanalyser psychiatriser psychologiser psychotiser
 publiciser pucher puddler puer puériliser puiser pulluler pulser pulvériser
 punaiser puncturer pupiniser pupuler puriner puruler puter putoiser putter
 pyramider pyrograver pyrolyser pyrrhoniser quadriller quadripolariser
 quadrupler quarderonner quarrer quarter quartiler quémander quereller querner
 questionner quêter queurser queuter quiller quimper quintupler quitter
 quoailler quotter rabâcher rabaisser rabaner rabanter rabibocher rabioter
 râbler raboter rabouiller rabouler rabouter rabreuver rabrouer raccastiller
 raccommoder raccompagner raccorder raccoutrer raccoutumer raccrocher racémiser
 rachalander racher raciner racketter racler râcler racoler raconter racoquiner
 radariser rader radicaliser radiner radioactiver radiobaliser radiocommander
 radioconserver radiodétecter radiodiffuser radioexposer radioguider
 radio-immuniser radiolocaliser radiopasteuriser radiosonder radiostériliser
 radiotéléphoner radiotéléviser radoter radouber rafaler raffermer raffiler
 raffiner raffluer raffoler raffûter rafistoler rafler ragoter ragoûter
 ragrafer raguer raguser raiguiser railler rainer rainurer raisonner rajouter
 rajuster râler ralinguer raller rallumer râloter ramailler ramarder ramarrer
 ramastiquer rambiner ramender ramer rameuter ramoner ramper ramser rancarder
 rançonner randomiser randoniser randonner randonniser ranimer rapapilloter
 rapatronner raper râper rapetisser rapiater rapiner rappareiller rapper
 rappliquer rapporter rapprêter rapprivoiser rapprocher rapprovisionner
 rapsoder raquer raser rassembler rassoter rassurer ratatiner rater ratiboiser
 ratiner ratiociner rationaliser rationner ratisser ratonner rattacher
 rattaquer rattirer rattraper raturer raucher raugmenter rauquer ravaler
 ravauder ravigoter raviner raviser ravitailler raviver rayonner réabdiquer
 réabonner réaborder réabouter réabreuver réabriter réabsenter réabsorber
 réaccaparer réaccepter réaccidenter réacclimater réaccorder réaccoster
 réaccoutumer réaccuser réachalander réacheminer réacquitter réactionner
 réactiver réactualiser réadapter réadditionner réadministrer réadmonester
 réadonner réadopter réaffecter réaffermer réafficher réaffiler réaffirmer
 réaffronter réaffûter reaganiser réagglutiner réaggraver réagrafer réagresser
 réaiguiller réaiguillonner réaimanter réaimer réajourner réajuster
 réalcooliser réalerter réaligner réalimenter réaliser réallaiter réallouer
 réallumer réamarrer réamender réamidonner réanalyser réanastomoser réanimer
 réannexer réannoter réapaiser réapostropher réapparenter réappliquer réapposer
 réapprécier réappréhender réapprivoiser réapprouver réapprovisionner réapurer
 réarchitecturer réargenter réargumenter réarmer réarnaquer réarpenter
 réarrêter réarroser réarticuler réasphalter réaspirer réassaisonner réassigner
 réassister réassumer réassurer réastiquer réattaquer réattiser réattribuer
 réauditionner réaugmenter réautomatiser réautoriser réavaler réavaliser
 rebâcher rebachoter rebâcler rebadigeonner rebâfrer rebaigner rebâillonner
 rebaiser rebaisoter rebaisser rebalader rebaliser rebancher rebander
 rebaptiser rebaratiner rebarber rebarbouiller rebarder rebarrer rebarricader
 rebasculer rebavarder rebêcher rebécoter rebecquer rebeller rébellionner
 rebétonner rebeurrer rebiffer rebiner rebioler rebipolariser rebiquer
 rebisouter rebizouter reblackbouler reblesser reblinder rebloquer rebobiner
 reboiser rebombarder rebomber rebooster reborder rebosser rebotter reboucher
 reboucler reboulonner rebourrer reboursicoter rebousculer rebouter reboutonner
 reboxer rebraguetter rebrancher rebraquer rebricoler rebrider rebriguer
 rebriller rebriser rebrocher rebroder rebronzer rebrosser rebrouiller
 rebrousser rebrûler rebûcher rebudgétiser rebuffer rebuller rebureaucratiser
 rebuter recâbler recacher recadrer recalaminer recalculer recaler recalfater
 recalfeutrer recalibrer recalquer recamoufler recamper recanaliser recanner
 recanonner recaoutchouter recapitaliser récapituler recapoter recaptiver
 recapturer recaractériser recarburer recarder recaresser recaser recasquer
 recataloguer recatégoriser recatholiciser recauser recavaler recaver receler
 recéler recenser recensurer recentraliser recentrer receper recéper
 réceptionner recercler recerner rechagriner rechamailler rechambouler
 rechanter rechantonner rechaper réchapper rechaptaliser recharpenter
 rechauffer réchauffer rechauler rechaumer rechausser réchelonner rechercher
 rechiader rechiffrer rechigner rechiper rechristianiser rechromer rechuter
 recibler récidiver réciproquer recirculer recirer reciter réciter reclamer
 réclamer reclientéliser récliner recliquer recloisonner reclôturer reclouer
 recoder recogner recoiffer recoïncider récoler recollaborer recollecter
 recollectiviser recoller recolliger récolliger recoloniser recolorer
 recolporter récolter recoltiner recombiner recommander recommémorer
 recommenter recommercialiser recommissionner recommuniquer recompartimenter
 recompenser récompenser recompiler recomplimenter recompliquer recomploter
 recomposer recompter recompulser reconcentrer reconceptualiser reconcrétiser
 recondamner recondenser reconditionner reconfesser reconfigurer reconfirmer
 reconfisquer réconforter reconfronter reconjuguer reconnecter reconsacrer
 reconseiller reconserver reconsigner reconsoler reconsolider reconspirer
 reconstater reconstituer reconsulter recontacter reconter recontingenter
 recontinuer recontracter recontrecarrer recontrer recontribuer reconverser
 reconvoquer recoordonner recoquiller recorder recorroborer recoter recoucher
 recouillonner recouler recoulisser recouper recouponner recourber recourtiser
 recouvrer recracher recraquer recravater recrédibiliser recréer récréer
 recreuser recrier récrier récriminer recristalliser recritiquer recroiser
 recroquer recroqueviller recrucifier recruter recuisiner reculer reculotter
 recultiver récurer récuser recycler redaller redamer redanser redater
 redéballer redébarbouiller redébarquer redébaucher redébiner redébloquer
 redébobiner redéborder redéboucher redébourser redébouter redébrancher
 redébrouiller redébroussailler redébudgétiser redébureaucratiser redécaisser
 redécaler redécalquer redécanter redécaper redécapoter redécentraliser
 redécerner redéchausser redéchiffrer redéchirer redécider redéclarer
 redécliner redécoder redécoiffer redécoller redécoloniser redécolorer
 redécompter redéconcentrer redéconnecter redéconner redéconseiller redécorer
 redécouler redécouper redécrocher redécrypter redéculotter redéfausser
 redéfavoriser redéfiler redéfricher redéfriper redéfriser redéfroisser
 redégivrer redégonfler redégotter redégringoler redégrouper redéjeuner
 redélimiter redélivrer redemander redémarrer redémêler redéminer
 redémissionner redémobiliser redémocratiser redémonter redémultiplier
 redénicher redénombrer redénouer redépanner redépeigner redépenser redéplisser
 redéporter redéposer redépouiller redérailler redérober redéserter redésirer
 redésister redesserrer redessiner redétacher redétailler redétecter
 redétériorer redéterminer redéterrer redévaler redévaliser redévaloriser
 redévaluer redévaster redévisser redévoiler redialoguer redicter rediffuser
 redimensionner rédimer rediminuer redîner rediscerner rediscuter redisjoncter
 redisloquer redispenser redisperser redisposer redisputer redistiller
 redistinguer redistribuer réditer rediviser redominer redompter redonder
 redonner redoper redorer redorloter redoser redoter redoubler redouter
 redresser redynamiser réécarter rééchafauder rééchelonner rééchouer rééclairer
 rééconomiser réécourter réécouter réécrouer réédicter rééditer rééduquer
 réeffectuer rééjecter réélaborer réélaguer réemballer réembarquer réembaucher
 réembobiner réemboîter réembourber réembouteiller réembrigader réémerger
 réémigrer réemmailloter réemmancher réemmêler réemmerder réémonder réemparer
 réempêcher réempêtrer réempiler réempocher réempoisonner réempoissonner
 réemprisonner réemprunter réencaisser réencaustiquer réencercler réenchaîner
 réenchanter réenchâsser réenchevêtrer réenclencher réencoder réencombrer
 réendetter réendosser réénergétiser réenfiler réenflammer réenfourcher
 réenfourner réengendrer réenglober réengouffrer réengraisser réenjamber
 réenliser réenquêter réenregistrer réenrhumer réenrouler réentamer réentartrer
 réenterrer réenthousiasmer réentortiller réentourer réentraîner réentrer
 réenvelopper réenvenimer réenvoler réenvoûter réépargner réépiler rééplucher
 réépouser rééquilibrer rééquiper réériger réescalader réescamoter réescompter
 réescorter réestimer réétaler réétamer réétatiser réétoffer réévaluer
 réévangéliser réévoquer réexalter réexaminer rééxaminer réexcuser réexécuter
 réexhiber réexhorter réexpérimenter réexpertiser réexpirer réexpliciter
 réexpliquer réexploiter réexplorer réexporter réexposer réexprimer réexpulser
 réextrader refabriquer refâcher refaçonner refacturer refamiliariser refarter
 refasciser refaucher refaufiler refavoriser reféliciter reféminiser refermer
 refêter refeuiller reficher refidéliser refiler refilmer refiltrer
 refiscaliser reflamber reflancher reflanquer réflectoriser réflexionner
 réflexiviser reflotter refluer refluxer refoirer refonder reforer reforester
 reformaliser reformater reformer réformer réformiser reformuler refouiller
 refouler refourgonner refourrer réfracter refranchiser refranciser refrapper
 refréner réfréner refringuer refriper refriser refrogner refroisser refrotter
 refuguer refumer refuser réfuter regâcher regaffer regagner regalber régaler
 regaloper regambader regarder regarer régater regazonner regénérer régenter
 regerber regermer regimber régimenter régimer régionaliser registrer
 réglementer reglisser regober regommer regonfler regoudronner regourer
 regoûter regrader regratter regraver regreffer regrêler régresser regretter
 regriffer regriller regrimper regrogner regronder regrouper regueuler
 régulariser réguler régurgiter réhabiliter réhabiter réhabituer réharmoniser
 rehasarder rehausser réhausser rehériter rehiérarchiser rehomologuer
 réhomologuer rehospitaliser réhospitaliser réhydrater réillustrer réimaginer
 réimbiber réimbriquer réimperméabiliser réimplanter réimpliquer réimplorer
 réimporter réimportuner réimposer réimprimer réimproviser réimpulser réimputer
 réincarner réinciser réincomber réincorporer réincruder réincuber réinculper
 réinculquer réindemniser réindexer réindustrialiser réinfecter réinféoder
 réinfester réinfiltrer réinformatiser réingurgiter réinhiber réinitialiser
 réinjecter réinsister réinsonoriser réinspecter réinspirer réinstaller
 réinstaurer réinstituer réinsuffler réintenter réintercaler réintercepter
 réintéresser réinterner réinterviewer réintituler réinventer réinviter
 réislamiser réitalianiser rejalonner rejetonner rejouer rejudaïser relabourer
 relâcher relaisser relarguer relater relatiniser relationner relativiser
 relatter relaver relaxer relégender relégitimer relifter relimer reliquider
 relisser relocaliser relooker relouer relouper reluquer relustrer relutter
 remâcher remaçonner remailer remailler remaîtriser remajorer remaltraiter
 remandater remanifester remanoeuvrer remaquiller remarchander remarcher
 remarquer remartyriser remasquer remastériser remastiquer remasturber
 remballer rembarquer rembarrer rembaucher rembiner remblaver rembobiner
 remboîter remborder rembourrer rembourser rembucher remédicaliser remêler
 remembrer remémorer rementionner remesurer remeubler remilitariser reminer
 reminéraliser reminuter remiser remixer remmailler remmailloter remmancher
 remmouler remobiliser remoderniser remondialiser remonétiser remonter
 remontrer remoquetter remorquer remotiver remotoriser remoucher remouiller
 remouler rempailler remparer rempiler remplumer rempocher rempoisonner
 rempoissonner remporter rempoter remprisonner remuer remurmurer remuscler
 renâcler renarder renationaliser renatter renaturaliser renauder renaviguer
 rencaisser rencarder renchausser rencogner rencoller rencontrer rencoquiller
 rencorser rendetter rendosser rêner rénetter renfaîter renfermer renfiler
 renflammer renfler renflouer renformer renfourner renfrogner rengainer
 rengraisser rengrener rengréner renifler renommer renoper renormaliser renoter
 renouer rénover renquiller renseigner renserrer rentabiliser rentamer renter
 rentoiler rentortiller rentraîner rentrer renucléariser renvelopper renvenimer
 renverser renvider renvoler réobserver réobstruer réobturer réoccuper
 réorchestrer réordonner réorganiser réorienter réoxyder repaginer repairer
 repapilloter reparapher repardonner reparer réparer reparler reparticiper
 répartonner repatiner repaumer repaver repavillonner repêcher repeigner
 repeinturer repencher repenser repercuter répercuter reperforer
 reperméabiliser repersonnaliser reperturber répétailler repéter répéter
 repétitionner repeupler rephosphorer repiler repiller repiloter repiocher
 repiquer repirater repisser repistonner replacarder replaider replaisanter
 replanquer replanter replaquer replastiquer replâtrer repleurer repleuvoter
 répliquer replisser replomber repointer repoisser repoivrer repolariser
 repolitiser repolluer repomper reponchonner reponctionner repopulariser
 reporter reposer repositionner repositiver repostuler repoudrer repousser
 repratiquer reprêcher repréciser repréparer représenter représider reprêter
 réprimander réprimer repriser reprivatiser reprocher reproclamer reprofaner
 reprofiler reprofiter reprogrammer reprogresser reprohiber reproposer
 repropulser reprouver réprouver reprovincialiser repter républicaniser
 répugner repuiser réputer requadriller requestionner requêter requiller
 requinquer réquisitionner rerespirer resabler resaboter resaccader
 resacraliser resaler resaluer resaper resauter resavonner rescaper resceller
 rescinder resélectionner reseller resensibiliser réserver résider resiffler
 resignaler resigner résigner résiner résister resituer reslaviser resocialiser
 resoigner resolliciter résonner résorber resouder resouper respectabiliser
 respecter respéculer respirer responsabiliser resquiller ressaigner ressaler
 ressangler ressauter ressembler resserrer ressouder ressuer ressusciter
 restabiliser restatuer restaurer rester restituer restoubler restructurer
 resubdiviser resuccomber resucrer resulfater résulter résumer résupiner
 resuppurer resurchauffer resyllaber resymboliser resympathiser resynchroniser
 resyndicaliser resyndiquer retacher retailler rétamer retanner retaper
 retapisser retarder retarifer retaxer retéléphoner retéléviser retémoigner
 retenter reterritorialiser reterser retester rethéâtraliser retimbrer retirer
 retisser retomber retoquer rétorquer retortiller retorturer retoucher retouper
 retourner retousser rétracter retrafiquer retraîner retraiter retrancher
 retransborder retransformer retransfuser retransiter retranspirer
 retransporter retransposer retransvaser retravailler retraverser retremper
 rétribuer retricher retricoter retrifouiller retrimbaler retrimballer
 retriompher retriturer rétroactiver rétrodiffuser rétrograder rétromorphoser
 retromper rétroréflectoriser rétroréguler retrotter retrouer retrousser
 retrouver rétroverser retruander retuer returbiner réunionner réusiner
 réutiliser revacciner revalider revaloriser revalser revancher revasculariser
 réveiller réveillonner revéler revendiquer reventer rêver reverbaliser
 revercher reverser revider revigorer revirer reviser réviser revisionner
 revisiter revisser revitaliser revoler révolter révolutionnariser
 révolutionner revolvériser révolvériser révoquer revoter revriller révulser
 rewriter rhabiller rhabiter rhabituer rhétoriquer rhumer ribauder ribler
 riblonner riboter ribouldinguer ribouler ricaner ricocher rider ridiculiser
 riduler riffauder rifler rigoler rimailler rimer ringarder ringardiser rinker
 rioter ripailler riper ripoliner riposter riser risquer rissoler ristourner
 ritter ritualiser rivaliser river rivotter rober robinsonner robotiser
 rocailler rocher rocker rocouer rocquer rôdailler roder rôder rogner rognonner
 rognurer rôler romaniser romantiser ronchonner ronder ronéoter ronéotyper
 ronfler ronfloter ronflotter ronronner ronsardiser roquer roser rosifier
 rosser rossignoler roter rotomouler rouanner roublarder roublardiser roucouer
 roucouler roucouyer rouer rouiller roulader rouler roulotter roumaniser
 roupiller rouscailler roussiller roussoter rouster rousturer router routiner
 rubaner rubriquer rucher rudenter ruer ruginer ruiler ruiner ruminer rupiner
 ruraliser rurbaniser ruser russiser rustiquer rutiler rythmer sabbatiser
 sabiriser sabler sablonner saborder saboter sabouler sabrer saccader
 sacchariner sacquer sacraliser sacrer sadiser safariser safraner saietter
 saigner sailler saisonner salabrer salariser saler salicyler saligoter saliner
 saliniser saliver salonner saloper salpêtrer salpêtriser saluer sanctionner
 sanctuariser sandwicher sanforiser sangler sangloter sanskritiser saoudiser
 saouler saoûler saper saquer sarabander sarcelliser sarcler sarmenter sarper
 sarrasiner sarter sataner sataniser satelliser satiner satiriser satoner
 satonner saturer satyriser saucissonner saumoner saumurer sauner saupoudrer
 saurer saussuritiser sauter sautiller sauvegarder sauver savater savonner
 savourer sayetter scalper scandaliser scander scandinaviser scanner
 scannériser sceller scénariser scheider schelinguer scheloter schématiser
 schizophréniser schlaguer schlinguer schlitter schloffer schloter schtroumpfer
 scientifiser scinder scintiller sciotter scissionner scléroser scolariser
 scooper scorer scotcher scotomiser scotomoser scrabbler scraber scratcher
 scribler scribouiller scripter scruter scrutiner sculpter secondariser
 seconder secouer secréter sécréter sectifier sectionner sectoriser séculariser
 sécuriser sédentariser sédimenter segmenter seiner séjourner sélecter
 sélectionner seller sémantiser sembler sémiller sempler sénégaliser senner
 sensationnaliser sensibiliser sentimentaliser séparer septembriser septupler
 séquestrer serbiser sérénader sérialiser seriner seringuer sermonner serpenter
 serpentiniser serper serrer sexer sextupler sexualiser sganarelliser
 shampoigner shampooiner shampooingner shampouiner shérardiser shooter shunter
 siallitiser siccativer siester siffler siffloter sigler signaler signaliser
 signer silhouetter silicater silicatiser siliciurer siliconer siller sillonner
 siloter similer similiser simonizer simuler sinapiser singulariser siniser
 sinistrer sinocentriser sintériser sinuer siphonner siroper siroter situer
 skipper slalomer slaviser smasher smiller smocker smurfer sniffer snober
 sociabiliser socialiser socratiser soder sodomiser soiffer soigner solariser
 solder soléciser solenniser solidariser solifluer soliloquer solliciter
 solmiser solubiliser solutionner solvabiliser somatiser sombrer sommeiller
 sommer somnambuler somniloquer somnoler sonder sonnailler sonner sonoriser
 sophistiquer sorguer soubresauter souder souffler souffroter soufrer souhaiter
 souiller souillonner soûler souligner soûlotter soumissionner soupailler
 soupçonner souper soupirer souquer sourciller sourdiner sous-alimenter
 sous-capitaliser sous-catégoriser sous-équiper sousestimer sous-estimer
 sous-évaluer sous-exploiter sous-exposer sous-industrialiser sous-louer
 sous-médicaliser sousperformer sous-qualifier soussigner sous-titrer
 sous-traiter sous-utiliser sous-virer soutacher souter soutirer soviétiser
 spammer spasmer spatialiser spatuler spécialiser spéculer sphéroïdiser
 spilitiser spiraler spiraliser spirantiser spiritualiser spitter
 splénectomiser spléniser sponsoriser sporter sporuler sprinter squatériser
 squatter squatteriser squattériser squeezer stabiliser stabuler staffer
 stagner staliniser standardiser standoliser stanioler stariser stationner
 statistiquer statuer stelliter stenciler stendhaliser sténoser sténotyper
 stepper stéréotyper stériliser stigmatiser stimuler stipuler stocker
 stoloniser stopper stranguler stratégiser stresser strider striduler striper
 stripper striquer stronker strouiller structurer strychniser stuquer styler
 styliser subalterniser subdiviser subdivisionner subériser subjectiver
 subjectiviser subjuguer sublimer sublimiser subluxer subminiaturiser subodorer
 subordonner suborner subsister substanter substantialiser substantiver
 substituer subsumer subtiliser suburbaniser subventionner succomber suçoter
 sucrer sudifier suer suffixer suffoquer suggestionner suicider suifer suiffer
 suinter sulfater sulfiniser sulfinuser sulfiter sulfoner sulfurer sulfuriser
 super supérioriser superposer superviser supplanter supplémenter supporter
 supposer supprimer suppurer supputer surabonder suraccumuler suractiver
 suradapter suradministrer suraffiner surajouter suralcooliser suralimenter
 suraller suranimer suranner surapposer surarmer surassister surbaisser
 surblinder surbooker surboucher surbriller surbroder surcapitaliser
 surchaptaliser surchauffer surcoller surcolorer surcommenter surcompenser
 surcomprimer surconsommer surcontrer surcoter surcouper surcreuser
 surdensifier surdéterminer surdévelopper surdimensionner surdorer surdoser
 surdouer suréchantillonner suréduquer surémanciper surencombrer surendetter
 surentraîner suréquilibrer suréquiper surestimer surévaluer surexciter
 surexhausser surexploiter surexposer surfacturer surfer surficher surfiler
 surfractionner surfrapper surgeonner surgonfler surgreffer surhausser
 surimposer surimpressionner surimprimer surindustrialiser suriner surinfecter
 surinformer surinterpréter surjauler surjouailler surjouer surligner surlouer
 surmécaniser surmédiatiser surmédicaliser surmédicamenter surmilitariser
 surmoduler surmonter surmouler surnaturaliser surnommer suroccidentaliser
 suroccuper suroxyder surpatter surpénaliser surperformer surpeupler surpiquer
 surplomber surpolitiser surpolluer surpresser surreprésenter surréserver
 sursaler sursaturer sursauter sursimuler sursouffler surstabiliser surstimuler
 surstocker sursulfater surtaxer surtitrer sururbaniser surutiliser
 survaloriser surveiller surventer survider survirer survitaminer survoler
 survolter susciter susmentionner suspecter susseyer sustanter sustenter
 susurrer suturer swaper swinguer sycotiser syllaber syllabiser syllogiser
 symbiotiser symboliser symétriser sympathiser synchroniser syncoper
 syncrétiser syncristalliser syndicaliser syndiquer synthétiser syntoniser
 syphiliser syrianiser systématiser tabiser tabler tabouer tabouiser tabuler
 tacher tâcher tacler taconner taffer taguer taillader tailler taler taller
 talocher talonner talquer taluter tambouiller tambouriner tamiser tamponner
 tangenter tanguer taniser tanner tanniser tantaliser taper tapiner tapirer
 tapiriser tapisser taponner tapoter taquer taquiner taquonner tarabiscoter
 tarabuster tararer tarauder tarder tarer targetter targuer tarifer
 tarmacadamiser tarter tartiner tartrer tartriquer tatariser tatillonner
 tâtonner tatouer tatouiller tauder tautologiser tautomériser taveller taxer
 tayloriser tchatcher techniciser techniser technocratiser tectoniser teiller
 teinter télécommander télédébiter télédétecter télédiffuser télédiriger
 téléfalsifier téléguider téléimprimer télélocaliser télémanipuler télématiser
 télépancarter téléphoner télépiloter téléporter télescoper téléscoper
 télésignaliser télésuggérer télésurveiller télétraiter téléviser télexer
 télomériser témoigner tempêter temporiser tenailler tenonner ténoriser
 tensionner tenter tergiverser terminer terrailler terreauder terreauter terrer
 terriner territorialiser terroriser terser tertiairiser tertiariser tester
 testonner tétaniser tétonner tétuer texturer texturiser théâtraliser
 thématiser théologiser théoriser thermaliser thermiser thermocoller
 thermodiffuser thermofixer thermoformer thermopropulser thermovinifier
 thésauriser thromboser thyroïdectomiser tictacquer tictaquer tigrer tiller
 tilloter tillotter tilter timbrer tinter tintinabuler tintinnabuler tiquer
 tirailler tirebouchonner tirefonner tirer tiser tisonner tisser titaner
 titaniser titiller titrer titriser tituber titulariser toaster toiler
 toiletter toiser tolstoïser toluiser tomater tomber tomer tonitruer tonner
 tonsurer tontiner tonturer toper topicaliser toquer torchecuter torcher
 torchonner torgnoler toronner torpiller torsader torsiner tortiller
 tortillonner tortorer torturer tosser toster totaliser totalitariser toucher
 touer touffer touiller toupiller toupiner tourber tourbillonner tourer
 tourillonner tourmenter tournailler tournaser tournebouler tourner tournevirer
 tournicoter tourniller tournioler tourniquer toussailler tousser toussoter
 trabouler tracaner trachéotomiser tracter tractionner traficoter trafiquer
 trafuser trailler traînailler traîner trainouiller traiter tramer trancaner
 tranchefiler trancher tranquilliser transbahuter transborder transcender
 transcoder transfecter transfigurer transfiler transformer transfuser
 transgresser transhumer transistoriser transiter translater transmigrer
 transmuer transmuter transnationaliser transpirer transplanter transporter
 transposer transsuder transvaser transvider trapper traquer traumatiser
 travailler travailloter traverser trébucher tréfiler treillisser trekker
 trélinguer trémater trembler tremblocher trembloter trémousser tremper
 trémuler trépaner trépider trépigner trésailler tressauter tresser treuiller
 trévirer trianguler tribaliser triballer tribouiller tricher tricoter
 trifouiller trigauder trigonaliser triller trimarder trimbaler trimballer
 trimer trimériser trimestrialiser tringler trinquer triompher tripatouiller
 tripler triploïdiser tripolisser tripotailler tripoter tripper triquer trisser
 triturer trivialiser trochisquer trognonner trôler trombiner tromboner tromper
 troncher tronçonner trôner tronquer tropicaliser troquer trotter trottiner
 troubler trouer trouiller troussequiner trousser trouver truander trucher
 trucider truculer trueller truffer truiter truquer trusquiner truster tuber
 tuberculiniser tuberculiser tubériser tuer tuiler tumultuer tunnelliser
 turbiner turboforer turkiser turlupiner turluter turquiser tuteurer tuyauter
 twister twitter tympaniser tyndalliser typer typiser tyranniser ukrainiser
 ultracentraliser ultrafiltrer ultraminiaturiser ululer uniatiser uniformiser
 universaliser upériser urbaniser uriner usager user usiner usiter usurper
 utiliser utopiser vacciner vacher vaciller vacuoliser vadrouiller vagabonder
 vaguer vaigrer vaironner valdinguer valider valiser vallonner valoriser valser
 vamper vampiriser vandaliser vaniser vanner vanter vantiler vantiller
 vapocraquer vaporiser vapoter vaquer varander varapper variabiliser varianter
 varioliser varloper vasculariser vasectomiser vaseliner vaser vasotomiser
 vasouiller vassaliser vaticiner vautrer vedettiser végétaliser véhiculer
 veiller veiner vélariser vêler vélivoler velouter velter vendiquer venter
 ventiler ventouser ventriloquer ventrouiller verbaliser verduniser vergner
 verjuter vermiculer vermiller vermillonner vermouler vernaliser vernisser
 véroter verrer verrouiller verser vert-de-griser vertébrer verticaliser vesser
 vétiller vexer viabiliser viander vibrer vibrionner victimer victimiser
 vidéosurveiller vider vidimer vieller vietnamiser vigiler vigiliser vignetter
 vilipender villagiser villégiaturer vinaigrer viner vingtupler violenter
 violer violoner virer virevolter virevousser virevouster virginiser virguler
 viriliser viroler virtualiser virusser viser visionner visiter visser
 visualiser vitaliser vitaminer vitaminiser vitrer vitrioler vitrioliser
 vivisecter vivoter vobuler vocaliser voguer voiler voiser voisiner voiturer
 volanter volatiliser volcaniser voler volontariser voltaïser volter voluter
 voter vouer vousser voûter voyeller voyelliser vriller vrillonner vulcaniser
 vulgariser vulnérabiliser warranter wobbuler xéroxer yodiser yodler yorubaïser
 youyouter yoyotter zader zaïrianiser zapper zéolitiser zéroter zester zieuter
 zigouiller zigzaguer zinguer zinzinuler zipper zombifier zoner zonzonner
 zoomer zozoter zyeuter
""".split()
)
