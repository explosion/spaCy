import React from 'react'
import PropTypes from 'prop-types'
import { StaticQuery, graphql } from 'gatsby'
import classNames from 'classnames'

import Link from './link'
import Grid from './grid'
import Newsletter from './newsletter'
import ExplosionLogo from '-!svg-react-loader!../images/explosion.svg'
import classes from '../styles/footer.module.sass'

export default function Footer({ wide = false }) {
    return (
        <StaticQuery
            query={query}
            render={data => {
                const { companyUrl, company, footer, newsletter } = data.site.siteMetadata
                return (
                    <footer className={classes.root}>
                        <Grid cols={wide ? 4 : 3} narrow className={classes.content}>
                            {footer.map(({ label, items }, i) => (
                                <section key={i}>
                                    <ul className={classes.column}>
                                        <li className={classes.label}>{label}</li>
                                        {items.map(({ text, url }, j) => (
                                            <li key={j}>
                                                <Link to={url} hidden>
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
                                <Link to={companyUrl} hidden>
                                    {company}
                                </Link>
                            </span>
                            <Link
                                to={companyUrl}
                                aria-label={company}
                                hidden
                                className={classes.logo}
                            >
                                <ExplosionLogo width={45} height={45} />
                            </Link>
                            <Link to={`${companyUrl}/legal`} hidden>
                                Legal / Imprint
                            </Link>
                        </div>
                    </footer>
                )
            }}
        />
    )
}

Footer.propTypes = {
    wide: PropTypes.bool,
}

const query = graphql`
    query FooterQuery {
        site {
            siteMetadata {
                company
                companyUrl
                footer {
                    label
                    items {
                        text
                        url
                    }
                }
                newsletter {
                    user
                    id
                    list
                }
            }
        }
    }
`
