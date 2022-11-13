import React from 'react'

import Accordion from './components/accordion'
import Aside from './components/aside'
import Button from './components/button'
import { InlineCode, Pre, TypeAnnotation } from './components/code'
import { GoogleSheet, Iframe, Image, SoundCloud, YouTube } from './components/embed'
import Grid from './components/grid'
import Infobox from './components/infobox'
import Link from './components/link'
import { Li, Ol, Ul } from './components/list'
import Section, { Hr } from './components/section'
import { Table, Td, Th, Tr, Tx } from './components/table'
import Tag from './components/tag'
import { Abbr, H2, H3, H4, H5, Help, Paragraph } from './components/typography'
import { Integration, IntegrationLogo } from './widgets/integration'
import Project from './widgets/project'

export const remarkComponents = {
    createElement: React.createElement,
    components: {
        a: Link,
        p: Paragraph,
        pre: Pre,
        // code: Code,
        code: InlineCode,
        pre: Pre,
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

        infobox: Infobox,
        table: Table,
        tr: Tr,
        tx: Tx,
        th: Th,
        td: Td,
        help: Help,
        button: Button,
        youtube: YouTube,
        soundcloud: SoundCloud,
        iframe: Iframe,
        googlesheet: GoogleSheet,
        abbr: Abbr,
        tag: Tag,
        accordion: Accordion,
        grid: Grid,
        inlinecode: InlineCode,
        project: Project,
        integration: Integration,
        integrationlogo: IntegrationLogo,
    },
}
