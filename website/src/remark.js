import Link from './components/link'
import Section, { Hr } from './components/section'
import { Table, Tr, Th, Tx, Td } from './components/table'
import { Pre, Code, InlineCode, TypeAnnotation } from './components/code'
import { Ol, Ul, Li } from './components/list'
import { H2, H3, H4, H5, P, Abbr, Help } from './components/typography'
import Accordion from './components/accordion'
import Infobox from './components/infobox'
import Aside from './components/aside'
import Button from './components/button'
import Tag from './components/tag'
import Grid from './components/grid'
import { YouTube, SoundCloud, Iframe, Image, GoogleSheet } from './components/embed'
import Project from './widgets/project'
import { Integration, IntegrationLogo } from './widgets/integration'

export const remarkComponents = {
    a: Link,
    p: P,
    pre: Pre,
    code: Code,
    inlineCode: InlineCode,
    del: TypeAnnotation,
    table: Table,
    img: Image,
    tr: Tr,
    th: Th,
    td: Td,
    ol: Ol,
    ul: Ul,
    li: Li,
    h2: H2,
    h3: H3,
    h4: H4,
    h5: H5,
    blockquote: Aside,
    section: Section,
    wrapper: ({ children }) => children,
    hr: Hr,

    Infobox,
    Table,
    Tr,
    Tx,
    Th,
    Td,
    Help,
    Button,
    YouTube,
    SoundCloud,
    Iframe,
    GoogleSheet,
    Abbr,
    Tag,
    Accordion,
    Grid,
    InlineCode,
    Project,
    Integration,
    IntegrationLogo,
}
