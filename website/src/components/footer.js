import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import SVG from 'react-inlinesvg'

import Link from './link'
import Grid from './grid'
import Newsletter from './newsletter'
import explosionLogo from '../images/explosion.svg'
import classes from '../styles/footer.module.sass'
import siteMetadata from '../../meta/site.json'

export default function Footer({ wide = false }) {
    const { companyUrl, company, footer, newsletter } = siteMetadata
    return (
        <footer className={classes.root}>
            <Grid cols={wide ? 4 : 3} narrow className={classes.content}>
                {footer.map(({ label, items }, i) => (
                    <section key={i}>
                        <ul className={classes.column}>
                            <li className={classes.label}>{label}</li>
                            {items.map(({ text, url }, j) => (
                                <li key={j}>
                                    <Link to={url} noLinkLayout>
                                        {text}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </section>
                ))}
                <section className={wide ? null : classes.full}>
                    <ul className={classes.column}>
                        <li className={classes.label}>Stay in the loop!</li>
                        <li>Receive updates about new releases, tutorials and more.</li>
                        <li>
                            <Newsletter {...newsletter} />
                        </li>
                    </ul>
                </section>
            </Grid>
            <div className={classNames(classes.content, classes.copy)}>
                <span>
                    &copy; 2016-{new Date().getFullYear()}{' '}
                    <Link to={companyUrl} noLinkLayout>
                        {company}
                    </Link>
                </span>
                <Link to={companyUrl} aria-label={company} noLinkLayout className={classes.logo}>
                    <SVG src={explosionLogo.src} width={45} height={45} />
                </Link>
                <Link to={`${companyUrl}/legal`} noLinkLayout>
                    Legal / Imprint
                </Link>
            </div>
        </footer>
    )
}

Footer.propTypes = {
    wide: PropTypes.bool,
}
