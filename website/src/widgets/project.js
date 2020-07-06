import React from 'react'

import CopyInput from '../components/copy'
import Infobox from '../components/infobox'
import Link from '../components/link'
import { InlineCode } from '../components/code'

// TODO: move to meta?
const DEFAULT_REPO = 'https://github.com/explosion/projects'
const COMMAND = 'python -m spacy project clone'

const Project = ({ id, repo, children }) => {
    const repoArg = repo ? ` --repo ${repo}` : ''
    const text = `${COMMAND} ${id}${repoArg}`
    const url = `${repo || DEFAULT_REPO}/${id}`
    const title = (
        <>
            🪐 Get started with a project template:{' '}
            <Link to={url}>
                <InlineCode>{id}</InlineCode>
            </Link>
        </>
    )
    return (
        <Infobox title={title}>
            {children}
            <CopyInput text={text} prefix="$" />
        </Infobox>
    )
}

export default Project
