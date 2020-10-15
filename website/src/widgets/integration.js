import React from 'react'

import Card from '../components/card'

import { ReactComponent as DVCLogo } from '../images/logos/dvc.svg'
import { ReactComponent as ProdigyLogo } from '../images/logos/prodigy.svg'
import { ReactComponent as StreamlitLogo } from '../images/logos/streamlit.svg'
import { ReactComponent as FastAPILogo } from '../images/logos/fastapi.svg'
import { ReactComponent as WandBLogo } from '../images/logos/wandb.svg'
import { ReactComponent as RayLogo } from '../images/logos/ray.svg'

const LOGOS = {
    dvc: DVCLogo,
    prodigy: ProdigyLogo,
    streamlit: StreamlitLogo,
    fastapi: FastAPILogo,
    wandb: WandBLogo,
    ray: RayLogo,
}

export const IntegrationLogo = ({ name, title, width, height, maxWidth, align, ...props }) => {
    const Logo = LOGOS[name]
    if (!Logo) throw new Error(`Unknown logo: ${name}`)
    const style = { maxWidth, float: align || 'none' }
    return (
        <Logo
            aria-label={title}
            aria-hidden={title ? undefined : 'true'}
            width={width}
            height={height}
            style={style}
            {...props}
        />
    )
}

export const Integration = ({ height = 30, url, logo, title, children }) => {
    const header = logo && (
        <IntegrationLogo name={logo} title={title} height={height} width="auto" maxWidth="80%" />
    )
    return (
        <Card title={header} to={url} small>
            {children}
        </Card>
    )
}
