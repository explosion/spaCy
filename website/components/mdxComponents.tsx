import { remarkComponents } from '../src/markdown'
import Architecture101 from '../docs/usage/101/_architecture.mdx'
import LanguageData101 from '../docs/usage/101/_language-data.mdx'
import NER101 from '../docs/usage/101/_named-entities.mdx'
import Pipelines101 from '../docs/usage/101/_pipelines.mdx'
import PosDeps101 from '../docs/usage/101/_pos-deps.mdx'
import Serialization101 from '../docs/usage/101/_serialization.mdx'
import Tokenization101 from '../docs/usage/101/_tokenization.mdx'
import Training101 from '../docs/usage/101/_training.mdx'
import Vectors101 from '../docs/usage/101/_vectors-similarity.mdx'
import Changelog from '../src/widgets/changelog.js'
import Features from '../src/widgets/features.js'
import { IntegrationLogo, Integration } from '../src/widgets/integration.js'
import Languages from '../src/widgets/languages.js'
import Project from '../src/widgets/project.js'
import QuickstartInstall from '../src/widgets/quickstart-install.js'
import QuickstartTraining from '../src/widgets/quickstart-training.js'
import QuickstartModels from '../src/widgets/quickstart-models.js'

const mdxComponents = {
    ...remarkComponents.components,

    Changelog,
    Features,
    IntegrationLogo,
    Integration,
    Languages,
    Project,
    QuickstartInstall,
    QuickstartTraining,
    QuickstartModels,

    Architecture101,
    LanguageData101,
    NER101,
    Pipelines101,
    PosDeps101,
    Serialization101,
    Tokenization101,
    Training101,
    Vectors101,
}

export default mdxComponents
