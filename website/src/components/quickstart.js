import React, { Fragment, useState, useEffect, useRef, Children } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { window, document } from 'browser-monads'

import Section from './section'
import Icon from './icon'
import { H2 } from './typography'
import { copyToClipboard } from './copy'
import classes from '../styles/quickstart.module.sass'

function getNewChecked(optionId, checkedForId, multiple) {
    if (!multiple) return [optionId]
    if (checkedForId.includes(optionId)) return checkedForId.filter((opt) => opt !== optionId)
    return [...checkedForId, optionId]
}

const Quickstart = ({
    data = [],
    title,
    description,
    copy = true,
    download,
    rawContent = null,
    id = 'quickstart',
    setters = {},
    showDropdown = {},
    hidePrompts,
    small,
    codeLang,
    Container = Section,
    children,
}) => {
    const contentRef = useRef()
    const copyAreaRef = useRef()
    const isClient = typeof window !== 'undefined'
    const supportsCopy = isClient && document.queryCommandSupported('copy')
    const showCopy = supportsCopy && copy
    const [checked, setChecked] = useState({})
    const [initialized, setInitialized] = useState(false)
    const [copySuccess, setCopySuccess] = useState(false)
    const [otherState, setOtherState] = useState({})
    const setOther = (id, value) => setOtherState({ ...otherState, [id]: value })
    const getRawContent = (ref) => {
        if (rawContent !== null) return rawContent
        if (ref.current && ref.current.childNodes) {
            // Select all currently visible nodes (spans and text nodes)
            const result = [...ref.current.childNodes].filter((el) => el.offsetParent !== null)
            return result.map((el) => el.textContent).join('\n')
        }
        return ''
    }

    const onClickCopy = () => {
        copyAreaRef.current.value = getRawContent(contentRef)
        copyToClipboard(copyAreaRef, setCopySuccess)
    }

    useEffect(() => {
        window.dispatchEvent(new Event('resize')) // scroll position for progress
        if (!initialized) {
            const initialChecked = Object.assign(
                {},
                ...data.map(({ id, options = [] }) => ({
                    [id]: options.filter((option) => option.checked).map(({ id }) => id),
                }))
            )
            setChecked(initialChecked)
            setInitialized(true)
        }
    }, [data, initialized])

    const isRelevant = (child) => {
        if (typeof child === 'string' || child.type !== QS) {
            return true
        }

        return data.every((itemData) => {
            return (
                !child.props[itemData.id] ||
                !checked[itemData.id] ||
                checked[itemData.id].includes(child.props[itemData.id])
            )
        })
    }

    return !data.length ? null : (
        <Container id={id}>
            <div
                className={classNames(classes['root'], {
                    [classes['hide-prompts']]: !!hidePrompts,
                })}
            >
                {title && (
                    <H2 className={classes['title']} name={id}>
                        <a href={`#${id}`}>{title}</a>
                    </H2>
                )}

                {description && <p className={classes['description']}>{description}</p>}

                {data.map(
                    ({
                        id,
                        title,
                        options = [],
                        dropdown = [],
                        defaultValue,
                        multiple,
                        other,
                        help,
                        hidden,
                    }) => {
                        // Optional function that's called with the value
                        const setterFunc = setters[id] || (() => {})
                        // Check if dropdown should be shown
                        const dropdownGetter = showDropdown[id] || (() => true)
                        return hidden ? null : (
                            <div key={id} data-quickstart-group={id} className={classes['group']}>
                                <div className={classes['legend']}>
                                    {title}
                                    {help && (
                                        <span data-tooltip={help} className={classes['help']}>
                                            {' '}
                                            <Icon name="help" width={16} />
                                        </span>
                                    )}
                                </div>
                                <div className={classes['fields']}>
                                    {options.map((option) => {
                                        const optionType = multiple ? 'checkbox' : 'radio'
                                        const checkedForId = checked[id] || []
                                        return (
                                            <Fragment key={option.id}>
                                                <input
                                                    onChange={() => {
                                                        const newChecked = {
                                                            ...checked,
                                                            [id]: getNewChecked(
                                                                option.id,
                                                                checkedForId,
                                                                multiple
                                                            ),
                                                        }
                                                        setChecked(newChecked)
                                                        setterFunc(newChecked[id])
                                                    }}
                                                    type={optionType}
                                                    className={classNames(
                                                        classes['input'],
                                                        classes[optionType]
                                                    )}
                                                    name={id}
                                                    id={`quickstart-${option.id}`}
                                                    value={option.id}
                                                    checked={checkedForId.includes(option.id)}
                                                />
                                                <label
                                                    className={classes['label']}
                                                    htmlFor={`quickstart-${option.id}`}
                                                >
                                                    {option.title}
                                                    {option.meta && <span>{option.meta}</span>}
                                                    {option.help && (
                                                        <span
                                                            data-tooltip={option.help}
                                                            className={classes['help']}
                                                        >
                                                            {' '}
                                                            <Icon name="help" width={16} />
                                                        </span>
                                                    )}
                                                </label>
                                            </Fragment>
                                        )
                                    })}
                                    <span className={classes['field-extra']}>
                                        {!!dropdown.length && (
                                            <select
                                                defaultValue={defaultValue}
                                                className={classNames(classes['select'], {
                                                    [classes['select-hidden']]: !dropdownGetter(),
                                                })}
                                                onChange={({ target }) => {
                                                    const value = target.value
                                                    if (value != other) {
                                                        setterFunc(value)
                                                        setOther(id, false)
                                                    } else {
                                                        setterFunc('')
                                                        setOther(id, true)
                                                    }
                                                }}
                                            >
                                                {dropdown.map(({ id, title }) => (
                                                    <option key={id} value={id}>
                                                        {title}
                                                    </option>
                                                ))}
                                                {other && <option value={other}>{other}</option>}
                                            </select>
                                        )}
                                        {other && otherState[id] && (
                                            <input
                                                type="text"
                                                className={classes['text-input']}
                                                placeholder="Type here..."
                                                onChange={({ target }) => setterFunc(target.value)}
                                            />
                                        )}
                                    </span>
                                </div>
                            </div>
                        )
                    }
                )}
                <pre className={classes['code']}>
                    <code>
                        <div
                            className={classNames(classes['results'], {
                                [classes['small']]: !!small,
                                [`language-${codeLang}`]: !!codeLang,
                            })}
                            data-quickstart-results=""
                            ref={contentRef}
                        >
                            {Children.toArray(children).flat().filter(isRelevant)}
                        </div>
                    </code>

                    <menu className={classes['menu']}>
                        {showCopy && (
                            <button
                                title="Copy to clipboard"
                                onClick={onClickCopy}
                                className={classes['icon-button']}
                            >
                                <Icon width={18} name={copySuccess ? 'accept' : 'clipboard'} />
                            </button>
                        )}
                        {download && (
                            <a
                                href={`data:application/octet-stream,${encodeURIComponent(
                                    getRawContent(contentRef)
                                )}`}
                                title="Download file"
                                download={download}
                                className={classes['icon-button']}
                            >
                                <Icon width={18} name="download" />
                            </a>
                        )}
                    </menu>
                </pre>
                {showCopy && (
                    <textarea
                        ref={copyAreaRef}
                        className={classes['copy-area']}
                        rows={1}
                        aria-label={`Interactive code example for ${title}`}
                    />
                )}
            </div>
        </Container>
    )
}

Quickstart.propTypes = {
    title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    data: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.string.isRequired,
            title: PropTypes.string.isRequired,
            multiple: PropTypes.bool,
            options: PropTypes.arrayOf(
                PropTypes.shape({
                    id: PropTypes.string.isRequired,
                    title: PropTypes.string.isRequired,
                    checked: PropTypes.bool,
                    help: PropTypes.string,
                })
            ),
            help: PropTypes.string,
        })
    ),
}

const QS = ({ children, prompt = 'bash', divider = false, comment = false, ...props }) => {
    const qsClassNames = classNames({
        [classes['prompt']]: !!prompt && !divider,
        [classes['bash']]: prompt === 'bash' && !divider,
        [classes['python']]: prompt === 'python' && !divider,
        [classes['divider']]: !!divider,
        [classes['comment']]: !!comment,
    })
    return <span className={qsClassNames}>{children}</span>
}

export { Quickstart, QS }
