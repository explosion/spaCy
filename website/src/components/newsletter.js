import React from 'react'
import PropTypes from 'prop-types'

import classes from '../styles/newsletter.module.sass'

export default function Newsletter({ user, id, list }) {
    const action = `//${user}.list-manage.com/subscribe/post?u=${id}&amp;id=${list}`
    return (
        <form
            id="mc-embedded-subscribe-form"
            name="mc-embedded-subscribe-form"
            action={action}
            method="post"
            target="_blank"
            noValidate
        >
            {/* MailChimp spam protection */}
            <div style={{ position: 'absolute', left: '-5000px' }} aria-hidden="true">
                <input type="text" name={`b_${id}_${list}`} tabIndex="-1" defaultValue="" />
            </div>

            <div className={classes.root}>
                <input
                    className={classes.input}
                    id="mce-EMAIL"
                    type="email"
                    name="EMAIL"
                    placeholder="Your email"
                    aria-label="Your email"
                />
                <button
                    className={classes.button}
                    id="mc-embedded-subscribe"
                    type="submit"
                    name="subscribe"
                >
                    Sign up
                </button>
            </div>
        </form>
    )
}

Newsletter.propTypes = {
    user: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    list: PropTypes.string.isRequired,
}
