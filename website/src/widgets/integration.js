import React from 'react'

import Card from '../components/card'

import DVCLogo from '-!svg-react-loader!../images/logos/dvc.svg'
import ProdigyLogo from '-!svg-react-loader!../images/logos/prodigy.svg'
import StreamlitLogo from '-!svg-react-loader!../images/logos/streamlit.svg'
import FastAPILogo from '-!svg-react-loader!../images/logos/fastapi.svg'
import WandBLogo from '-!svg-react-loader!../images/logos/wandb.svg'
import RayLogo from '-!svg-react-loader!../images/logos/ray.svg'
import HuggingFaceHubLogo from '-!svg-react-loader!../images/logos/huggingface_hub.svg'

const LOGOS = {
    dvc: DVCLogo,
    prodigy: ProdigyLogo,
    streamlit: StreamlitLogo,
    fastapi: FastAPILogo,
    wandb: WandBLogo,
    ray: RayLogo,
    huggingface_hub: HuggingFaceHubLogo,
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
