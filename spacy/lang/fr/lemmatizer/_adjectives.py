# coding: utf8
from __future__ import unicode_literals


ADJECTIVES = set("""
 abaissant abaissé abandonné abasourdi abasourdissant abattu abcédant aberrant
 abject abjurant aboli abondant abonné abordé abouti aboutissant abouté
 abricoté abrité abrouti abrupt abruti abrutissant abruzzain absent absolu
 absorbé abstinent abstrait abyssin abâtardi abêtissant abîmant abîmé acarpellé
 accablé accalminé accaparant accastillant accentué acceptant accepté accidenté
 accolé accombant accommodant accommodé accompagné accompli accordé accorné
 accoudé accouplé accoutumé accrescent accroché accru accréditant accrédité
 accueillant accumulé accusé accéléré acescent achalandé acharné achevé
 acidulé aciéré acotylé acquitté activé acuminé acutangulé acutifolié acutilobé
 adapté additionné additivé adextré adhérent adimensionné adiré adjacent
 adjoint adjugé adjuvant administré admirant adné adolescent adoptant adopté
 adossé adouci adoucissant adressé adroit adscrit adsorbant adultérin adéquat
 affaibli affaiblissant affairé affamé affectionné affecté affermi affidé
 affilé affin affligeant affluent affolant affolé affranchi affriolant affronté
 affété affûté afghan africain agaillardi agatin agatisé agaçant agglomérant
 agglutinant agglutiné aggravant agissant agitant agité agminé agnat agonisant
 agrafé agrandi agressé agrippant agrégé agréé aguichant ahanant ahuri
 aigretté aigri aigrissant aiguilleté aiguisé ailé aimant aimanté aimé ajourné
 ajusté alabastrin alambiqué alangui alanguissant alarmant alarmé albuginé
 alcalescent alcalifiant alcalin alcalinisant alcoolisé aldin alexandrin alezan
 aligoté alizé aliénant aliéné alkylant allaitant allant allemand allergisant
 alliciant allié allongé allumant allumé alluré alléchant allégeant allégé
 alphabloquant alphastimulant alphonsin alpin alternant alternifolié
 altérant altéré alucité alvin alvéolé alésé amaigri amaigrissant amalgamant
 amaril ambiant ambisexué ambivalent ambulant ami amiantacé amiantin amidé
 aminé ammoniacé ammoniaqué ammonié amnistiant amnistié amnésiant amoindrissant
 amorti amplifiant amplifié amplié ampoulé amputé amusant amusé amylacé
 américain amérisant anabolisant analgésiant anamorphosé anarchisant anastigmat
 anavirulent ancorné andin andorran anergisant anesthésiant angevin anglican
 angoissant angoissé angustifolié angustipenné animé anisé ankylosant ankylosé
 anobli anoblissant anodin anovulant ansé ansérin antenné anthropisé
 antialcalin antiallemand antiamaril antiautoadjoint antibrouillé
 anticipant anticipé anticoagulant anticontaminant anticonvulsivant
 antidécapant antidéflagrant antidérapant antidétonant antifeutrant
 antigivrant antiglissant antiliant antimonié antiméthémoglobinisant antinatal
 antiodorant antioxydant antiperspirant antiquisant antirassissant
 antiréfléchissant antirépublicain antirésonant antirésonnant antisymétrisé
 antivieillissant antiémétisant antécédent anténatal antéposé antérieur
 antérosupérieur anémiant anémié aoûté apaisant apeuré apicalisé aplati apocopé
 apparent apparenté apparié appartenant appaumé appelant appelé appendiculé
 appointé apposé apprivoisé approchant approché approfondi approprié approuvé
 apprêté appuyé appétissant apérianthé aquarellé aquitain arabisant araucan
 arborisé arboré arcelé archaïsant archiconnu archidiocésain architecturé
 ardent ardoisé ardu argentin argenté argilacé arillé armoricain armé
 arpégé arqué arrangeant arrivant arrivé arrogant arrondi arrosé arrêté arsénié
 articulé arénacé aréolé arétin ascendant ascosporé asexué asin asphyxiant
 aspirant aspiré assaillant assainissant assaisonné assassin assassinant
 asservissant assidu assimilé assistant assisté assiégeant assiégé associé
 assommant assonancé assonant assorti assoupi assoupissant assouplissant
 assujetti assujettissant assuré asséchant astreignant astringent atloïdé
 atonal atrophiant atrophié attachant attaquant attardé atteint attenant
 attendu attentionné atterrant attesté attirant attitré attrayant attristant
 atélectasié auriculé auscitain austral authentifiant autoadjoint autoagrippant
 autoancré autobronzant autocentré autocohérent autocollant autocommandé
 autocontraint autoconvergent autocopiant autoflagellant autofondant autoguidé
 autolubrifiant autolustrant autolégitimant autolégitimé automodifiant
 autonettoyant autoportant autoproduit autopropulsé autorepassant autorisé
 autosuffisant autotrempant auvergnat avachi avalant avalé avancé avarié
 aventuriné aventuré avenu averti aveuglant avianisé avili avilissant aviné
 avivé avoisinant avoué avéré azimuté azoté azuré azéri aéronaval aéroporté
 aéré aîné babillard badaud badgé badin bahaï bahreïni bai baillonné baissant
 balafré balancé balbutiant baleiné ballant ballonisé ballonné ballottant
 balzan bambochard banal banalisé bancal bandant bandé bangladeshi banlieusard
 bantou baraqué barbant barbarisant barbelé barbichu barbifiant barbu bardé
 baroquisant barré baryté basané basculant basculé basedowifiant basedowifié
 bastillé bastionné bataillé batifolant battant battu bavard becqué bedonnant
 bellifontain belligérant benoît benzolé benzoïné berçant beurré biacuminé
 bicarbonaté bicarré bicomponent bicomposé biconstitué bicontinu bicornu
 bidonnant bienfaisant bienséant bienveillant bigarré bigot bigourdan bigéminé
 bilié billeté bilobé bimaculé binoclard biodégradant bioluminescent biorienté
 biparti bipectiné bipinné bipolarisé bipédiculé biramé birman biréfringent
 biscuité bisexué bismuthé bisontin bispiralé bissexué bisublimé bisérié
 biterné bivalent bivitellin bivoltin blafard blanchissant blanchoyant blasé
 blessé bleu bleuissant bleuté blindé blond blondin blondissant blondoyant
 blousant blâmant blêmissant bodybuildé boisé boitillant bombé bonard
 bondé bonifié bonnard borain bordant borin borné boré bossagé bossu bot
 bouclé boudiné bouffant bouffi bouillant bouilli bouillonnant boulant bouleté
 bouqueté bourdonnant bourdonné bourgeonnant bourrant bourrelé bourru bourré
 boutonné bovin bracelé bradycardisant braillard branchu branché branlant
 bressan bretessé bretonnant breveté briard bridgé bridé brillant brillanté
 bringueballant brinquebalant brinqueballant briochin brioché brisant brisé
 broché bromé bronzant bronzé brouillé broutant bruissant brun brunissant brut
 brévistylé brûlant brûlé budgeté burelé buriné bursodépendant busqué busé
 butyracé buté byzantin bâtard bâti bâté béant béat bédouin bégayant bénard
 bénédictin béquetant béquillard bétonné bêlant bêtabloquant bêtifiant bômé
 cabochard cabotin cabriolant cabré cacaoté cachectisant cachemiri caché
 cadjin cadmié caducifolié cafard cagnard cagot cagoulé cahotant caillouté
 calcicordé calcifié calculé calmant calotin calé camard cambrousard cambré
 camisard campagnard camphré campé camé canaliculé canin cannelé canné cantalou
 canulant cané caoutchouté capitolin capitulant capitulard capité capricant
 capsulé captivant capuchonné caquetant carabiné caracolant caractérisé
 carbonaté carboné carburant carburé cardiocutané cardé carencé caressant
 carillonnant carillonné carié carminé carné carolin caronculé carpé carré
 caréné casqué cassant cassé castelroussin castillan catalan catastrophé
 catégorisé caudé caulescent causal causant cavalcadant celtisant cendré censé
 centraméricain centré cerclé cerdagnol cerdan cerné certain certifié cervelé
 chafouin chagrin chagrinant chagriné chaloupé chamoisé chamoniard chancelant
 chantant chançard chapeauté chapé charançonné chargé charmant charnu charpenté
 charrié chartrain chassant chasé chatoyant chaud chauffant chaussant chauvin
 chenillé chenu chevalin chevauchant chevelu chevelé chevillé chevronné
 chiant chicard chiffonné chiffré chimioluminescent chimiorésistant chiné
 chié chlamydé chleuh chlorurant chloruré chloré chocolaté choisi choké
 choral chronodépendant chryséléphantin chuintant chypré châtain chélatant
 chômé ciblé cicatrisant cilié cinglant cinglé cintré circiné circonspect
 circonvoisin circulant circumtempéré ciré cisalpin cisjuran cispadan citadin
 citronné citérieur civil civilisé clabotant clair claironnant clairsemé
 clandestin clapotant claquant clarifiant clariné classicisant claudicant
 clavelé clignotant climatisé clinquant cliquetant clissé clivant cloisonné
 cloqué clouté cloîtré clément clémentin coagulant coalescent coalisé coassocié
 cocciné cocu codant codirigeant codominant codé codélirant codétenu coexistant
 cogné cohérent coiffant coiffé coinché cokéfiant colicitant colitigant
 collant collodionné collé colmatant colombin colonisé colorant coloré
 combattant combinant combinard combiné comburant comité commandant commençant
 commun communard communiant communicant communiqué communisant compact
 comparé compassé compatissant compensé complaisant complexant compliqué
 composant composé comprimé compromettant computérisé compétent comtadin conard
 concertant concerté conciliant concluant concomitant concordant concourant
 concupiscent concurrent concédant condamné condensant condensé condescendant
 conditionné condupliqué confiant confident confiné confit confondant confédéré
 congru congruent conjoint conjugant conjugué connaissant connard connivent
 conné conquassant conquérant consacrant consacré consanguin conscient conscrit
 conservé consistant consolant consolidé consommé consonant constant constellé
 constipant constipé constituant constitué constringent consultant conséquent
 containeurisé contaminant contemporain content contenu contestant continent
 continu contondant contourné contractant contraignant contraint contraposé
 contrarié contrastant contrasté contravariant contrecollé contredisant
 contrefait contrevariant contrevenant contrit controuvé controversé contrôlé
 convaincu convalescent conventionné convenu convergent converti convoluté
 convulsivant convulsé conçu cooccupant cooccurrent coopérant coordiné
 coordonné copartageant coparticipant coquillé coquin coraillé corallin
 cordé cornard corniculé cornu corné corpulent correct correspondant corrigé
 corrodant corrompu corrélé corticodépendant corticorésistant cortisoné
 coréférent cossard cossu costaud costulé costumé cotisant couard couchant
 coulant coulissant coulissé coupant couperosé couplé coupé courant courbatu
 couronnant couronné court courtaud courtisan couru cousu couturé couvert
 covalent covariant coïncident coûtant crachotant craché cramoisi cramponnant
 craquelé cravachant crawlé crevant crevard crevé criant criard criblant criblé
 crispant cristallin cristallisant cristallisé crochu croisetté croiseté
 croissanté croisé crollé croquant crossé crotté croulant croupi croupissant
 croyant cru crucifié cruenté crustacé cryodesséché cryoprécipité crémant
 crépi crépitant crépu crétacé crétin crétinisant créé crêpelé crêté cubain
 cuirassé cuisant cuisiné cuit cuivré culminant culotté culpabilisant cultivé
 cuscuté cutané cyanosé câblé câlin cédant célébrant cérulé cérusé cévenol
 damassé damné dandinant dansant demeuré demi dentelé denticulé dentu denté
 dessalé dessiccant dessillant dessiné dessoudé desséchant deutéré diadémé
 diamanté diapré diastasé diazoté dicarbonylé dichloré diffamant diffamé
 diffractant diffringent diffusant différencié différent différé difluoré
 diiodé dilatant dilaté diligent dilobé diluant dimensionné dimidié dimidé
 diminué diocésain diphasé diplômant diplômé direct dirigeant dirigé dirimant
 discipliné discontinu discord discordant discriminant discuté disert disgracié
 disloqué disodé disparu dispersant dispersé disposé disproportionné disputé
 dissimulé dissipé dissociant dissocié dissolu dissolvant dissonant disséminé
 distant distinct distingué distrait distrayant distribué disubstitué disulfoné
 divagant divaguant divalent divergent divertissant divin divorcé djaïn
 dodu dogmatisant dolent domicilié dominant dominicain donjonné donnant donné
 dormant dorsalisant doré douci doué drageonnant dragéifié drainant dramatisant
 drapé dreyfusard drogué droit dru drupacé dual ductodépendant dulcifiant dur
 duveté dynamisant dynamité dyspnéisant dystrophiant déaminé débarqué débauché
 débilitant débloquant débordant débordé débouchant débourgeoisé déboussolé
 débridé débrouillard débroussaillant débroussé débutant décadent décaféiné
 décalant décalcifiant décalvant décapant décapité décarburant décati décavé
 décevant déchagriné décharné déchaînant déchaîné déchevelé déchiqueté
 déchiré déchloruré déchu décidu décidué décidé déclaré déclassé déclenchant
 décoiffant décolleté décolorant décoloré décompensé décomplémenté décomplété
 déconcertant déconditionné déconfit décongestionnant déconnant déconsidéré
 décontractant décontracturant décontracté décortiqué décoré découplé découpé
 décousu découvert décrispant décrochant décroissant décrépi décrépit décuman
 décussé décérébré dédoré défaillant défait défanant défatigant défavorisé
 déferlant déferlé défiant déficient défigé défilant défini déflagrant défleuri
 défléchi défoliant défoncé déformant défranchi défraîchi défrisant défroqué
 défâché défécant déférent dégagé dégingandé dégivrant déglutiné dégonflé
 dégourdi dégouttant dégoûtant dégoûté dégradant dégradé dégraissant dégriffé
 déguisé dégénérescent dégénéré déhanché déhiscent déjeté délabrant délabré
 délassant délavé délayé délibérant délibéré délicat délinquant déliquescent
 délitescent délié déloqué déluré délégué démagnétisant démaquillant démaqué
 dément démerdard démesuré démixé démodé démontant démonté démoralisant
 démotivant démotivé démystifiant démyélinisant démyélisant démêlant dénaturant
 dénigrant dénitrant dénitrifiant dénommé dénudé dénutri dénué déodorant
 dépapillé dépareillé dépassé dépaysant dépaysé dépeigné dépenaillé dépendant
 dépeuplé déphasé dépité déplacé déplaisant déplaquetté déplasmatisé dépliant
 déplumant déplumé déplété dépoitraillé dépolarisant dépoli dépolitisant
 déponent déporté déposant déposé dépouillé dépourvu dépoussiérant dépravant
 déprimant déprimé déprédé dépérissant dépétainisé déracinant déraciné
 dérangé dérapant dérestauré dérivant dérivé dérobé dérogeant déroulant
 déréalisant déréglé désabusé désaccordé désadapté désaffectivé désaffecté
 désaisonnalisé désaligné désaliénant désaltérant désaluminisé désambiguïsé
 désargenté désarmant désarçonnant désassorti désatomisé désaturant désaxé
 désemparé désenchanté désensibilisant désert désespérant désespéré
 désherbant déshonorant déshumanisant déshydratant déshydraté déshydrogénant
 désiconisé désillusionnant désincarné désincrustant désinfectant
 désintéressé désirant désobligeant désoblitérant désobéi désobéissant
 désodorisant désodé désoeuvré désolant désolé désopilant désordonné
 désorienté désossé désoxydant désoxygénant déstabilisant déstressant
 désuni déséquilibrant déséquilibré détachant détaché détartrant détendu détenu
 déterminant déterminé déterré détonant détonnant détourné détraqué détérioré
 développé déverbalisant dévergondé déversé dévertébré déviant dévissé
 dévoisé dévolu dévorant dévot dévoué dévoyé déwatté déçu effacé effarant
 effarouché effaré effervescent efficient effiloché effilé efflanqué
 effluent effondré effrangé effrayant effrayé effronté effréné efféminé
 emballant embarrassant embarrassé embellissant embiellé embouché embouti
 embrassant embrassé embrouillant embrouillé embroussaillé embruiné embryonné
 embusqué embêtant emmerdant emmiellant emmiélant emmotté empaillé empanaché
 empenné emperlé empesé empiétant emplumé empoignant empoisonnant emporté
 empressé emprunté empâté empêché empêtré encaissant encaissé encalminé
 encapsulant encapsulé encartouché encastré encerclant enchanté enchifrené
 encloisonné encloqué encombrant encombré encorné encourageant encroué
 encroûté enculé endenté endiablé endiamanté endimanché endogé endolori
 endormi endurant endurci enfantin enfariné enflammé enflé enfoiré enfoncé
 engageant engagé engainant englanté englobant engoulé engourdi engourdissant
 engraissant engravé engrenant engrené engrêlé enguiché enhardé enivrant
 enjambé enjoué enkikinant enkysté enlaidissant enlaçant enlevé enneigé ennemi
 ennuyant ennuyé enquiquinant enracinant enrageant enragé enregistrant enrhumé
 enrichissant enrobé enseignant enseigné ensellé ensoleillé ensommeillé
 ensoutané ensuqué entartré entendu enterré enthousiasmant entouré entrant
 entraînant entrecoupé entrecroisé entrelacé entrelardé entreprenant entresolé
 entrouvert enturbanné enté entêtant entêté envahissant envapé enveloppant
 envenimé enviné environnant envié envoyé envoûtant ergoté errant erroné
 escarpé espacé espagnol espagnolisant esquintant esquinté esseulé essorant
 estomaqué estompé estropié estudiantin euphorisant euphémisé eurafricain
 exacerbé exact exagéré exalbuminé exaltant exalté exaspérant excellent
 excepté excitant excité exclu excluant excommunié excru excédant exempt
 exercé exerçant exfoliant exhalant exhilarant exigeant exilé exinscrit
 exondé exorbitant exorbité exosporé exostosant expansé expatrié expectant
 expert expirant exploitant exploité exposé expropriant exproprié expulsé
 expérimenté extasié extemporané extradossé extrafort extraplat extrapériosté
 extraverti extroverti exténuant extérieur exubérant exultant facilitant
 faiblissant faignant failli faillé fainéant faisandé faisant fait falot falqué
 fané faraud farci fardé farfelu farinacé fasciculé fascinant fascisant fascié
 fassi fastigié fat fatal fatigant fatigué fauché favorisant façonné faïencé
 feint fendant fendillé fendu fenestré fenian fenêtré fermant fermentant
 ferritisant ferruginisé ferré fertilisant fervent fescennin fessu festal
 festival feuillagé feuilleté feuillu feuillé feutrant feutré fiancé fibrillé
 ficelé fichant fichu fieffé figulin figuré figé filant fileté filoguidé
 filé fimbrié fin final finalisé finaud fini finissant fiérot flabellé flagellé
 flagrant flamand flambant flamboyant flambé flamingant flammé flanchard
 flanquant flapi flatulent flavescent flemmard fleurdelisé fleuri fleurissant
 flippant florentin florissant flottant flottard flotté flou fluctuant fluent
 fluidifié fluocompact fluorescent fluoré flushé fléchissant fléché flémard
 flétrissant flûté foisonnant foliacé folié folliculé folâtrant foncé fondant
 fondé forain foraminé forcené forcé forfait forgé formalisé formaté formicant
 formé fort fortifiant fortrait fortuit fortuné fossilisé foudroyant fouettard
 fouillé fouinard foulant fourbu fourcheté fourchu fourché fourmillant fourni
 foutral foutu foxé fracassant fractal fractionné fragilisant fragrant
 franchouillard francisant franciscain franciscanisant frangeant frappant
 fratrisé frelaté fretté friand frigorifié fringant fringué friqué frisant
 frisotté frissonnant frisé frit froid froissant froncé frondescent frottant
 froussard fructifiant fruité frumentacé frustrant frustré frutescent
 fréquent fréquenté frétillant fugué fulgurant fulminant fumant fumé furfuracé
 furibond fusant fuselé futur futé fuyant fuyard fâché fébricitant fécond
 féculent fédéré félin féminin féminisant férin férié féru fêlé gabalitain
 gagé gai gaillard galant galbé gallican gallinacé galloisant galonné galopant
 ganglionné gangrené gangué gantelé garant garanti gardé garni garnissant
 gauchisant gazonnant gazonné gazouillant gazé gaël geignard gelé genouillé
 germanisant germé gestant gesticulant gibelin gigotant gigotté gigoté girond
 gironné gisant gitan givrant givré glabrescent glacial glacé glandouillant
 glapissant glaçant glissant glissé globalisant glomérulé glottalisé
 gloussant gloutonnant gluant glucosé glycosylé glycuroconjugué godillé
 goguenard gommant gommé goménolé gondolant gonflant gonflé gouleyant goulu
 gourmand gourmé goussaut gouvernant gouverné goûtu goûté gradué gradé graffité
 grand grandiloquent grandissant granité granoclassé granulé graphitisant
 grasseyant gratifiant gratiné gratuit gravant gravitant greffant grelottant
 grenelé grenu grené griffu grignard grilleté grillé grimaçant grimpant
 grinçant grippé grisant grisonnant grivelé grondant grossissant grouillant
 grésillant gueulard guignard guilloché guillotiné guindé guivré guéri gâté
 gélatinisant gélatiné gélifiant gélifié géminé gémissant géniculé généralisant
 géométrisant gérant gênant gêné gîté habilitant habilité habillé habitué
 hachuré haché hagard halbrené haletant halin hallucinant halluciné hanché
 hanté harassant harassé harcelant harcelé hardi harpé hasté haut hautain
 hennissant heptaperforé herbacé herborisé herbu herminé hernié hersé heurté
 hibernant hilarant hindou hircin hispanisant historicisant historisant
 hivernant hiérosolymitain holocristallin hominisé homogénéisé homoprothallé
 homoxylé honorant honoré hordéacé hormonodéprivé horodaté horrifiant
 hottentot hoyé huguenot huitard humain humectant humiliant humilié huppé
 hutu hyalin hydratant hydrocarboné hydrochloré hydrocuté hydrogénant hydrogéné
 hydrosalin hydrosodé hydroxylé hyperalcalin hypercalcifiant hypercalcémiant
 hypercoagulant hypercommunicant hypercorrect hyperfin hyperfractionné
 hyperisé hyperlordosé hypermotivé hyperphosphatémiant hyperplan hypersomnolent
 hypertrophiant hypertrophié hypervascularisé hypnotisant hypoalgésiant
 hypocalcémiant hypocarpogé hypocholestérolémiant hypocotylé hypoglycémiant
 hypolipidémiant hypophosphatémiant hyposodé hypotendu hypotonisant
 hypovirulent hypoxémiant hâlé hébraïsant hébété hélicosporé héliomarin
 hélitransporté hémicordé hémicristallin hémiplégié hémodialysé hémopigmenté
 hépatostrié hérissant hérissé hésitant hétéroprothallé hétérosporé hétérostylé
 identifié idiot idiotifiant idéal ignifugeant ignorant ignorantin ignoré igné
 illimité illuminé imaginant imaginé imagé imbriqué imbrûlé imbu imité immaculé
 immergé immigrant immigré imminent immodéré immortalisant immotivé immun
 immunocompétent immunodéprimant immunodéprimé immunostimulant immunosupprimé
 immédiat immérité impair impaludé imparfait imparidigité imparipenné impatient
 impayé impensé imperforé impermanent imperméabilisant impertinent implorant
 important importun importé imposant imposé impotent impressionnant imprimant
 impromptu impromulgué improuvé imprudent imprévoyant imprévu impudent
 impuni impur impénitent impétiginisé inabordé inabouti inabrité inabrogé
 inaccepté inaccompli inaccoutumé inachevé inactivé inadapté inadéquat
 inaguerri inaliéné inaltéré inanalysé inanimé inanitié inapaisé inaperçu
 inapparenté inappliqué inapprivoisé inapproprié inapprécié inapprêté
 inarticulé inassimilé inassorti inassouvi inassujetti inattaqué inattendu
 inavoué incandescent incapacitant incarnadin incarnat incarné incendié
 incessant inchangé inchâtié incident incidenté incitant incivil inclassé
 incliné inclément incohérent incombant incomitant incommodant incommuniqué
 incompétent inconditionné inconfessé incongru incongruent inconnu inconquis
 inconsidéré inconsistant inconsolé inconsommé inconstant inconséquent
 incontesté incontinent incontrôlé inconvenant incoordonné incorporant
 incorrect incorrigé incriminant incriminé incritiqué incroyant incrustant
 incréé incubant inculpé incultivé incurvé indeviné indifférencié indifférent
 indirect indirigé indiscipliné indiscriminé indiscuté indisposé indistinct
 indolent indompté indou indu induit indulgent indupliqué induré
 indébrouillé indécent indéchiffré indécidué indéfini indéfinisé indéfriché
 indélibéré indélicat indémontré indémêlé indépassé indépendant indépensé
 indéterminé ineffectué inefficient inemployé inentamé inentendu inespéré
 inexaucé inexercé inexistant inexpert inexpié inexpliqué inexploité inexploré
 inexprimé inexpérimenté inexécuté infamant infantilisant infarci infatué
 infectant infecté infestant infesté infichu infiltrant infini inflammé
 infléchi infondé informant informulé infortuné infoutu infréquenté infusé
 inféodé inférieur inférovarié ingrat ingénu inhabité inhalant inhibant inhibé
 inhérent inimité inintelligent ininterrompu inintéressant initié injecté
 innervant innocent innominé innommé innomé innovant inné inobservé inoccupé
 inondé inopiné inopportun inopérant inorganisé inoublié inouï inquiétant
 insatisfait insaturé inscrit insensé insermenté insignifiant insinuant
 insolent insondé insonorisant insonorisé insouciant insoupçonné inspirant
 inspécifié installé instant instantané instructuré instruit insubordonné
 insulinodépendant insulinorésistant insultant insulté insurgé insécurisant
 intelligent intempérant intentionné interallié interaméricain intercepté
 intercristallin intercurrent interdigité interdiocésain interdit
 interfacé interfécond interférent interloqué intermittent intermédié interpolé
 interprétant intersecté intersexué interstratifié interurbain intervenant
 intestin intimidant intolérant intoxicant intoxiqué intramontagnard
 intrigant introduit introjecté introverti intumescent intégrant intégrifolié
 intéressé intérieur inusité inutilisé invaincu invalidant invariant invendu
 inverti invertébré inviolé invitant involucré involuté invérifié invétéré
 inéclairci inécouté inédit inégalé inélégant inéprouvé inépuisé inéquivalent
 iodoformé ioduré iodylé iodé ionisant iridescent iridié irisé ironisant
 irraisonné irrassasié irritant irrité irréalisé irréfléchi irréfuté irrémunéré
 irrésolu irrévélé islamisant isohalin isolant isolé isosporé issant issu
 itinérant ivoirin jacent jacobin jaillissant jamaïcain jamaïquain jambé
 japonné jardiné jarreté jarré jaspé jauni jaunissant javelé jaïn jobard joint
 joli joufflu jouissant jovial jubilant juché judaïsant jumelé juponné juré
 juxtaposant juxtaposé kalmouk kanak kazakh kenyan kosovar kératinisé labié
 lacinié lactant lactescent lactosé lacté lai laid lainé laité lambin lambrissé
 lamifié laminé lampant lampassé lamé lancinant lancé lancéolé languissant
 lapon laqué lardacé larmoyant larvé laryngé lassant latent latifolié latin
 latté latéralisé lauré lauréat lavant lavé laïcisant lent lenticulé letton
 lettré leucopéniant leucosporé leucostimulant levant levantin levretté levé
 liant libertin libéré licencié lichénifié liftant lifté ligaturé lignifié
 ligulé lilacé limacé limitant limougeaud limousin lionné lippu liquéfiant
 lithiné lithié lité lié liégé lobulé lobé localisé loculé lointain lombard
 lorrain loré losangé loti louchant loupé lourd lourdaud lubrifiant luisant
 lunetté lunulé luné lusitain lustré luthé lutin lutéinisant lutéostimulant
 lyophilisé lyré léché lénifiant léonard léonin léopardé lézardé maboul maclé
 madré mafflu maghrébin magnésié magnétisant magrébin magyar mahométan maillant
 majeur majorant majorquin maladroit malaisé malavisé malbâti malentendant
 malformé malintentionné malnutri malodorant malotru malouin malpoli malsain
 malséant maltraitant malté malveillant malvoyant maléficié mamelonné mamelu
 manchot mandarin mandchou maniéré mannité manoeuvrant manquant manqué mansardé
 mantouan manuscrit manuélin maori maraîchin marbré marcescent marchand
 marial marin mariol marié marmottant marocain maronnant marquant marqueté
 marquésan marrant marri martelé martyr marxisant masculin masculinisant
 masqué massacrant massant massé massétérin mat matelassé mati matérialisé
 maugrabin maugrebin meilleur melonné membrané membru menacé menant menaçant
 mentholé menu merdoyant mesquin messin mesuré meublant mexicain micacé
 microencapsulé microgrenu microplissé microéclaté miellé mignard migrant
 militant millerandé millimétré millésimé mineur minidosé minorant minorquin
 miraculé miraillé miraud mirobolant miroitant miroité miré mitigé mitré mité
 mobiliérisé mochard modelant modifiant modulant modulé modélisant modéré
 mogol moiré moisi moleté molletonné mollissant momentané momifié mondain mondé
 monilié monobromé monochlamydé monochloré monocomposé monocontinu
 monofluoré monogrammé monohalogéné monohydraté mononucléé monophasé
 monopérianthé monoréfringent monosporé monotriphasé monovalent montagnard
 montpelliérain monté monténégrin monumenté moralisant mordant mordicant
 mordu morfal morfondu moribond moricaud mormon mort mortifiant morvandiot
 mosellan motivant motivé mouchard moucheté mouflé mouillant mouillé moulant
 moulé mourant moussant moussu moustachu moutonnant moutonné mouvant mouvementé
 moyé mozambicain mucroné mugissant mulard multiarticulé multidigité
 multilobé multinucléé multiperforé multiprogrammé multirésistant multisérié
 multivalent multivarié multivitaminé multivoltin munificent murin muriqué
 murrhin musard musclé musqué mussipontain musulman mutant mutilant mutin
 myorelaxant myrrhé mystifiant mythifiant myélinisant myélinisé mâtiné méchant
 méconnu mécontent mécréant médaillé médian médiat médicalisé médisant
 méfiant mélangé mélanostimulant méningé méplat méprisant méritant mérulé
 métallescent métallisé métamérisé métastasé méthoxylé méthyluré
 métropolitain météorisant mêlé mûr mûrissant nabot nacré nageant nain naissant
 nanti napolitain narcissisant nasard nasillard natal natté naturalisé naufragé
 naval navigant navrant nazi nervin nervuré nervé nettoyant neumé neuralisant
 neuroméningé neutralisant nickelé nictitant nidifiant nigaud nigérian
 nippon nitescent nitrant nitrifiant nitrosé nitrurant nitré noir noiraud
 nombrant nombré nominalisé nommé nonchalant normalisé normand normodosé
 normotendu normé notarié nourri nourrissant noué noyé nu nuagé nuancé nucléolé
 nullard numéroté nutant nué né nébulé nécessitant nécrosant négligent négligé
 néoformé néolatin néonatal névrosant névrosé obligeant obligé oblitérant
 obscur observant obsolescent obstiné obstrué obsédant obsédé obséquent
 obturé obéi obéissant obéré occitan occupant occupé occurrent ocellé ochracé
 oculé odorant odoriférant oeillé oeuvé offensant offensé officiant offrant
 olivacé oléacé oléfiant oléifiant oman ombellé ombiliqué ombragé ombré
 omniprésent omniscient ondoyant ondulant ondulé ondé onglé onguiculé ongulé
 opalescent opalin operculé opiacé opportun opposant oppositifolié opposé
 oppressé opprimant opprimé opsonisant optimalisant optimisant opulent opérant
 orant ordonné ordré oreillard oreillé orfévré organisé organochloré
 organosilicié orientalisant orienté oropharyngé orphelin orthonormé ortié
 osmié ossifiant ossifluent ossu ostial ostracé ostrogot ostrogoth ostréacé osé
 ouaté ourlé oursin outillé outrageant outragé outrecuidant outrepassé outré
 ouvragé ouvrant ouvré ovalisé ovillé ovin ovulant ové oxycarboné oxydant
 oxygéné ozoné oïdié pacifiant padan padouan pahlavi paillard pailleté pair
 palatin palermitain palissé pallotin palmatilobé palmatinervé palmatiséqué
 palmiséqué palmé palpitant panaché panafricain panard paniculé paniquant panné
 pantelant pantouflard pané papalin papelard papilionacé papillonnant
 papou papyracé paraffiné paralysant paralysé paramédian parcheminé parent
 parfumé paridigitidé paridigité parigot paripenné parlant parlé parmesan
 parsi partagé partant parti participant partisan partousard partouzard
 parvenu paré passant passepoilé passerillé passionnant passionné passé pataud
 patelin patelinant patent patenté patient patoisant patriotard pattu patté
 paumé pavé payant pectiné pehlevi peigné peinard peint pelliculant pelliculé
 peluché pelé penaud penchant penché pendant pendu pennatilobé pennatinervé
 penninervé penné pensant pensionné pentavalent pentu peptoné perchloraté
 percutant percutané perdant perdu perfectionné perfolié perforant performant
 perfusé perlant perluré perlé permanent permutant perphosporé perruqué persan
 persistant personnalisé personnifié personé persuadé persulfuré persécuté
 pertinent perturbant perverti perçant pesant pestiféré petiot petit peul
 pharmocodépendant pharyngé phasé philippin philistin phophorylé phosphaté
 phosphoré photoinduit photoluminescent photorésistant photosensibilisant
 phénolé phénotypé piaffant piaillant piaillard picard picoté pigeonnant
 pignonné pillard pilonnant pilosébacé pimpant pinaillé pinchard pincé pinné
 pinçard pionçant piquant piqué pisan pistillé pitchoun pivotant piégé
 placé plafonnant plaidant plaignant plain plaisant plan planant planté plané
 plasmolysé plastifiant plat plein pleurant pleurard pleurnichard pliant
 plissé plié plombé plongeant plumeté pluriarticulé plurihandicapé plurinucléé
 plurivalent pochard poché poignant poilant poilu pointillé pointu pointé
 poitevin poivré polarisant polarisé poli policé politicard polluant
 polycarburant polychloré polycontaminé polycopié polycristallin polydésaturé
 polyhandicapé polyinsaturé polylobé polynitré polynucléé polyparasité
 polysubstitué polysyphilisé polytransfusé polytraumatisé polyvalent
 polyvoltin pommelé pommeté pompant pompé ponctué pondéré pontifiant pontin
 poplité poqué porcelainé porcin porracé portant portoricain possédant possédé
 postillonné postnatal postnéonatal posté postérieur posé potelé potencé
 poupin pourprin pourri pourrissant poursuivant pourtournant poussant poussé
 pratiquant prenant prescient prescrit pressant pressionné pressé prieur primal
 privilégié probant prochain procombant procubain profilé profitant profond
 programmé prohibé projetant prolabé proliférant prolongé prompt promu
 prononcé propané proportionné proratisé proscrit prostré protestant protonant
 protubérant protéiné provenant provocant provoqué proéminent prudent pruiné
 préalpin prébendé précipitant précipité précité précompact préconscient
 précontraint préconçu précuit précédent prédesséché prédestiné prédiffusé
 prédisposant prédominant prédécoupé préemballé préencollé préenregistré
 préfabriqué préfixé préformant préfragmenté préférant préféré prégnant
 prélatin prématuré prémuni prémédité prénasalisé prénatal prénommé préoblitéré
 préoccupé préparant prépayé prépondérant prépositionné préprogrammé préroman
 présalé présanctifié présent présignifié présumé présupposé prétendu
 prétraité prévalant prévalent prévenant prévenu prévoyant prévu préémargé
 préétabli prêt prêtant prêté psychiatrisé psychostimulant psychoénergisant
 puant pubescent pudibond puissant pulsant pulsé pultacé pulvérulent puni pur
 puritain purpuracé purpurin purulent pustulé putrescent putréfié puéril puîné
 pyramidant pyramidé pyrazolé pyroxylé pâli pâlissant pédant pédantisant
 pédiculosé pédiculé pédonculé pékiné pélorié pénalisant pénard pénicillé
 pénétrant pénétré péquenaud pérennant périanthé périgourdin périmé périnatal
 pérégrin pérégrinant péréqué pétant pétaradant pétillant pétiolé pétochard
 pétrifiant pétrifié pétré pétulant pêchant qatari quadrifolié quadrigéminé
 quadriparti quadrivalent quadruplété qualifiant qualifié quantifié quart
 questionné quiescent quinaud quint quintessencié quintilobé quiné quérulent
 rabattable rabattant rabattu rabougri raccourci racorni racé radiant radicant
 radiodiffusé radiolipiodolé radiorésistant radiotransparent radiotélévisé
 raffermissant raffiné rafraîchi rafraîchissant rageant ragot ragoûtant
 raisonné rajeunissant rallié ramassé ramenard ramifié ramolli ramollissant
 ramé ranci rangé rapatrié rapiat raplati rappelé rapporté rapproché rarescent
 rasant rassasiant rassasié rassemblé rassurant rassuré rassérénant rasé
 ratiocinant rationalisé raté ravageant ravagé ravalé ravi ravigotant ravissant
 rayé rebattu rebondi rebondissant rebutant recalé recarburant recercelé
 rechigné recombinant recommandé reconnaissant reconnu reconstituant recoqueté
 recroiseté recroquevillé recru recrudescent recrutant rectifiant recueilli
 redenté redondant redoublant redoublé refait refoulant refoulé refroidissant
 regardant regrossi reinté relaxant relevé reluisant relâché relégué remarqué
 rempli remuant renaissant renchéri rendu renfermé renflé renfoncé renforçant
 rengagé renommé rentrant rentré renté renversant renversé repentant repenti
 reporté reposant reposé repoussant repoussé repressé représentant repu
 resarcelé rescapé rescindant rescié respirant resplendissant ressemblant
 ressortissant ressurgi ressuscité restant restreint restringent resurgi
 retardé retentissant retenu retiré retombant retrait retraité retrayant
 retroussé revanchard revigorant revitalisant reviviscent reçu rhinopharyngé
 rhodié rhumatisant rhumé rhénan rhônalpin riant ribaud riboulant ricain
 riciné ridé rifain rigolard ringard risqué riverain roidi romagnol romain
 romand romanisant rompu rond rondouillard ronflant rongeant rosacé rossard
 rotacé roublard roucoulant rouergat rougeaud rougeoyant rougi rougissant
 rouleauté roulotté roulé roumain rouquin rousseauisant routinisé roué rubané
 rubicond rubéfiant rudenté rugissant ruiné ruisselant ruminant rupin rurbain
 rusé rutilant rythmé râblé râlant râpé réadapté réalisant récalcitrant récent
 réchauffant réchauffé récidivant récitant réclamant réclinant récliné
 réconfortant récurant récurrent récurvé récusant réduit réentrant réflectorisé
 réfléchissant réformé réfrigérant réfrigéré réfringent réfugié référencé
 régissant réglant réglé régnant régressé régénérant régénéré réhabilité
 réitéré réjoui réjouissant rémanent rémittent rémunéré rénitent répandu
 réprouvé républicain répugnant réputé réservé résidant résident résigné
 résiné résistant résolu résolvant résonant résonnant résorbant résorciné
 résumé résupiné résurgent rétabli rétamé réticent réticulé rétrofléchi
 rétroréfléchissant rétréci réuni réussi réverbérant révoltant révolté révolu
 révulsant révulsé révélé révérend rééquilibrant rêvé rôti sabin saccadé
 sacchariné sacrifié sacré safrané sagitté sahraoui saignant saignotant
 sain saint saisi saisissant saladin salant salarié salicylé salin salissant
 samaritain samoan sanctifiant sanglant sanglotant sanguin sanguinolent
 sanskrit santalin saoul saoulard saponacé sarrasin satané satiné satisfaisant
 saturant saturnin saturé saucissonné saucé saugrenu saumoné saumuré sautant
 sautillé sauté sauvagin savant savoyard scalant scarifié scellé sciant
 sclérosant sclérosé scolié scoriacé scorifiant scout script scrobiculé
 second secrétant semelé semi-fini sempervirent semé sensibilisant sensé senti
 serein serpentin serré servant servi seul sexdigité sexué sexvalent seyant
 sibyllin sidérant sifflant sigillé siglé signalé signifiant silicié silicosé
 simplifié simultané simulé sinapisé sinisant siphonné situé slavisant
 snobinard socialisant sociologisant sodé soiffard soignant soigné solognot
 somali sommeillant sommé somnolant somnolent sonnant sonné sorbonnard sortant
 souahéli soudain soudant soudé soufflant soufflé souffrant soufi soulevé
 sourd souriant soussigné soutenu souterrain souverain soûlant soûlard
 spatulé spermagglutinant spermimmobilisant sphacélé spiralé spirant spiritain
 splénectomisé spontané sporulé spumescent spécialisé stabilisant stagnant
 staphylin stationné stibié stigmatisant stigmatisé stimulant stipendié stipité
 stipulé stratifié stressant strict strident stridulant strié structurant
 stupéfait stupéfiant stylé sténohalin sténosant stérilisant stérilisé
 su suant subalpin subclaquant subconscient subintrant subit subjacent
 sublimant subneutralisant subordonnant subordonné subrogé subsident subséquent
 subulé suburbain subventionné subérifié succenturié succinct succulent
 sucrant sucré sucé suffisant suffocant suffragant suicidé suintant suivant
 sulfamidorésistant sulfamidé sulfaté sulfhydrylé sulfoné sulfurant sulfurisé
 superfin superfini superflu supergéant superhydratant superordonné superovarié
 suppliant supplicié suppléant supportant supposé suppurant suppuré
 supradivergent suprahumain supérieur surabondant suractivé surajouté suranné
 surbrillant surchargé surchauffé surclassé surcomposé surcomprimé surcouplé
 surdéterminant surdéterminé surdéveloppé surencombré surexcitant surexcité
 surfin surfondu surfrappé surgelé surgi surglacé surhaussé surhumain suri
 surmenant surmené surmultiplié surmusclé surneigé suroxygéné surperformé
 surplombant surplué surprenant surpressé surpuissant surréalisant sursalé
 sursaturé sursilicé surveillé survitaminé survivant survolté surémancipé
 susdit susdénommé susmentionné susnommé suspect suspendu susrelaté susurrant
 suzerain suédé swahili swahéli swazi swingant swingué sylvain sympathisant
 synanthéré synchronisé syncopé syndiqué synthétisant systématisé séant sébacé
 séchant sécurisant sécurisé séduisant ségrégué ségrégé sélectionné sélénié
 sémitisant sénescent séparé séquencé séquestrant sérigraphié séroconverti
 sérotonicodépendant sétacé sévillan tabou tabouisé tacheté taché tadjik taillé
 taloté taluté talé tamil tamisant tamisé tamoul tangent tannant tanné tapant
 tapissant taponné tapé taqueté taquin tarabiscoté taraudant tarentin tari
 tartré taré tassé tatar taupé taurin tavelé teint teintant teinté telluré
 tempérant tempéré tenaillant tenant tendu tentant ternifolié terraqué
 terrifiant terrorisant tessellé testacé texan texturant texturé thallosporé
 thermisé thermocollant thermodurci thermofixé thermoformé thermohalin
 thermoluminescent thermopropulsé thermorémanent thermorésistant thrombopéniant
 thrombosé thymodépendant thébain théocentré théorbé tibétain tiercé tigré tigé
 timbré timoré tintinnabulant tiqueté tirant tiré tisonné tissu titané titré
 tocard toisonné tolérant tombal tombant tombé tonal tondant tondu tonifiant
 tonnant tonsuré tonturé tophacé toquard toqué torché tordant tordu torsadé
 tortu torturant toscan totalisant totipotent touchant touffu toulousain
 tourelé tourmentant tourmenté tournant tournoyant tourné tracassant tracté
 traitant tramaillé tranchant tranché tranquillisant transafricain transalpin
 transandin transcendant transcutané transfini transfixiant transformant
 transi transloqué transmutant transpadan transparent transperçant transpirant
 transposé transtévérin transylvain trapu traumatisant traumatisé travaillant
 traversant travesti traçant traînant traînard treillissé tremblant tremblotant
 trempant trempé tressaillant triboluminescent tributant trichiné tricoté
 tridenté trifoliolé trifolié trifurqué trigéminé trilobé trin trinervé
 triparti triphasé triphosphaté trisubstitué tritié trituberculé triturant
 trivialisé trompettant tronqué troublant trouillard trouvé troué truand
 truffé truité trypsiné trébuchant tréflé trémulant trépassé trépidant
 tuant tubard tubectomisé tuberculé tubulé tubéracé tubérifié tubérisé tufacé
 tuilé tumescent tuméfié tuniqué turbiné turbocompressé turbulent turgescent
 tutsi tué twisté typé tâtonnant téflonisé téléphoné télévisé ténorisant
 térébrant tétraphasé tétrasubstitué tétravalent têtu tôlé ulcéré ultraciblé
 ultracourt ultrafin ultramontain ultérieur uncinulé unciné uni unifiant
 uniformisant unilobé uninucléé uniovulé unipotent uniramé uniréfringent
 unistratifié unisérié unitegminé univalent univitellin univoltin urbain
 urgent urticant usagé usant usité usé utriculé utérin utérosacré vacant
 vacciné vachard vacillant vadrouillant vagabond vagabondant vaginé vagissant
 vain vaincu vairé valdôtain valgisant validant vallonné valorisant valué
 valvé vanadié vanilliné vanillé vanisé vanné vantard variolé varisant varié
 varvé vasard vascularisé vasostimulant vasouillard vaudou veinard veiné
 velu venaissin venant vendu ventripotent ventromédian ventru venté verdissant
 vergeté verglacé verglaçant vergé verjuté vermicellé vermiculé vermoulant
 verni vernissé verré versant versé vert verticillé vertébré vespertin vexant
 vibrionnant vicariant vicelard vicié vieilli vieillissant vigil vigilant
 vigorisant vil vilain violacé violent violoné vipérin virevoltant viril
 virulent visigoth vitaminé vitellin vitré vivant viverrin vivifiant vivotant
 vogoul voilé voisin voisé volant volanté volatil voletant voltigeant volvulé
 vorticellé voulu voussé voyant voûté vrai vrillé vrombissant vu vulnérant
 vulturin vécu végétant véhément vélin vélomotorisé vérolé vésicant vésiculé
 vêtu wallingant watté wisigoth youpin zazou zend zigzagant zinzolin zoné
 zoulou zélé zézayant âgé ânonnant ébahi ébaubi éberlué éblouissant ébouriffant
 éburnin éburné écaillé écartelé écarté écervelé échancré échantillonné échappé
 échauffant échauffé échevelé échiqueté échoguidé échu éclairant éclaircissant
 éclatant éclaté éclipsant éclopé écoeurant écorché écoté écoutant écranté
 écrasé écrit écru écrémé éculé écumant édenté édifiant édulcorant égaillé
 égaré égayant égrillard égrisé égrotant égueulé éhanché éhonté élaboré élancé
 électrisant électroconvulsivant électrofondu électroluminescent
 élevé élingué élisabéthain élizabéthain éloigné éloquent élu élégant
 émacié émanché émancipé émarginé émergent émergé émerillonné émerveillant
 émigré éminent émollient émotionnant émoulu émoustillant émouvant ému
 émulsionnant éméché émétisant énergisant énervant énervé épaississant épanoui
 épargnant épatant épaté épeigné éperdu épeuré épicotylé épicutané épicé
 épigé épinglé éploré éployé épointé époustouflant épouvanté éprouvant éprouvé
 épuisé épuré équicontinu équidistant équilibrant équilibré équin équipollent
 équipolé équipotent équipé équitant équivalent éraillé éreintant éreinté
 érubescent érudit érythématopultacé établi étagé éteint étendu éthéré
 étiolé étoffé étoilé étonnant étonné étouffant étouffé étourdi étourdissant
 étriquant étriqué étroit étudiant étudié étymologisant évacuant évacué évadé
""".split())
