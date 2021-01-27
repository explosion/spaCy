import React from 'react'

import CopyInput from '../components/copy'
import Infobox from '../components/infobox'
import Link from '../components/link'
import { InlineCode } from '../components/code'
import { projectsRepo } from '../components/util'

const COMMAND = 'python -m spacy project clone'

export default function Project({
    title = 'Get started with a project template',
    id,
    repo,
    children,
}) {
    const repoArg = repo ? ` --repo ${repo}` : ''
    const text = `${COMMAND} ${id}${repoArg}`
    const defaultRepo = `https://github.com/${projectsRepo}`
    const url = `${repo || defaultRepo}/${id}`
    const header = (
        <>
            {title}:{' '}
            <Link to={url}>
                <InlineCode>{id}</InlineCode>
            </Link>
        </>
    )
    return (
        <Infobox title={header} emoji="🪐">
            {children}
            <CopyInput text={text} prefix="$" />
        </Infobox>
    )
}
