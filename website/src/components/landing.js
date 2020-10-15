import React from 'react'
import classNames from 'classnames'

import pattern from '../images/pattern_blue.jpg'
import patternNightly from '../images/pattern_nightly.jpg'
import patternOverlay from '../images/pattern_landing.jpg'
import patternOverlayNightly from '../images/pattern_landing_nightly.jpg'

import Grid from './grid'
import { Content } from './main'
import Button from './button'
import CodeBlock from './code'
import { H1, H2, H3 } from './typography'
import Link from './link'
import classes from '../styles/landing.module.sass'

export const LandingHeader = ({ nightly, style = {}, children }) => {
    const overlay = nightly ? patternOverlayNightly : patternOverlay
    const wrapperStyle = { backgroundImage: `url(${nightly ? patternNightly : pattern})` }
    const contentStyle = { backgroundImage: `url(${overlay})`, ...style }
    return (
        <header className={classes.header}>
            <div className={classes.headerWrapper} style={wrapperStyle}>
                <div className={classes.headerContent} style={contentStyle}>
                    {children}
                </div>
            </div>
        </header>
    )
}

export const LandingTitle = ({ children }) => <h1 className={classes.title}>{children}</h1>

export const LandingSubtitle = ({ children }) => (
    <h2>
        <span className={classNames(classes.label, classes.subtitle)}>{children}</span>
    </h2>
)

export const LandingGrid = ({ cols = 3, blocks = false, style, children }) => (
    <Content className={classNames({ [classes.blocks]: blocks })}>
        <Grid cols={cols} narrow={blocks} className={classes.grid} style={style}>
            {children}
        </Grid>
    </Content>
)

export const LandingCol = ({ children }) => <div className={classes.col}>{children}</div>

export const LandingCard = ({ title, button, url, children }) => (
    <div className={classes.card}>
        <section className={classes.cardText}>
            {title && <H3>{title}</H3>}
            <p>{children}</p>
        </section>
        {button && url && (
            <footer>
                <LandingButton to={url}>{button}</LandingButton>
            </footer>
        )}
    </div>
)

export const LandingButton = ({ to, children }) => (
    <Button to={to} variant="primary" large className={classes.button}>
        {children}
    </Button>
)

export const LandingDemo = ({ title, children }) => {
    return (
        <div className={classes.demo}>
            <CodeBlock executable lang="python" title={title}>
                {children}
            </CodeBlock>
        </div>
    )
}

export const LandingBannerGrid = ({ children }) => (
    <Grid cols={2} className={classes.bannerGrid}>
        {children}
    </Grid>
)

export const LandingBanner = ({
    title,
    label,
    to,
    button,
    small,
    background,
    backgroundImage,
    color,
    children,
}) => {
    const contentClassNames = classNames(classes.bannerContent, {
        [classes.bannerContentSmall]: small,
    })
    const textClassNames = classNames(classes.bannerText, {
        [classes.bannerTextSmall]: small,
    })
    const style = {
        '--color-theme': background,
        '--color-back': color,
        backgroundImage: backgroundImage ? `url(${backgroundImage})` : null,
    }
    const Heading = small ? H2 : H1
    return (
        <div className={classes.banner} style={style}>
            <Grid cols={small ? null : 3} narrow className={contentClassNames}>
                <Heading Component="h3" className={classes.bannerTitle}>
                    {label && (
                        <div className={classes.bannerLabel}>
                            <span className={classes.label}>{label}</span>
                        </div>
                    )}
                    <Link to={to} hidden>
                        {title}
                    </Link>
                </Heading>
                <div className={textClassNames}>
                    <p>{children}</p>

                    {button && (
                        <LandingBannerButton to={to} small={small}>
                            {button}
                        </LandingBannerButton>
                    )}
                </div>
            </Grid>
        </div>
    )
}

export const LandingBannerButton = ({ to, small, children }) => (
    <div className={classes.bannerButton}>
        <Button to={to} variant="tertiary" large={!small} className={classes.bannerButtonElement}>
            {children}
        </Button>
    </div>
)
