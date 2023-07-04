import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import CodeMirror from '@uiw/react-codemirror'
import { createTheme } from '@uiw/codemirror-themes'
import { tags as t } from '@lezer/highlight'
import { python } from '@codemirror/lang-python'
import { Kernel, ServerConnection } from '@jupyterlab/services'
import { window } from 'browser-monads'
import classes from '../styles/code.module.sass'

const spacyTheme = createTheme({
    theme: 'dark',
    settings: {
        background: 'var(--color-front)',
        foreground: 'var(--color-subtle-on-dark)',
        caret: 'var(--color-theme-dark)',
        selection: 'var(--color-theme-dark)',
        selectionMatch: 'var(--color-theme-dark)',
        gutterBackground: 'var(--color-front)',
        gutterForeground: 'var(--color-subtle-on-dark)',
        fontFamily: 'var(--font-code)',
    },
    styles: [
        { tag: t.comment, color: 'var(--syntax-comment)' },
        { tag: t.variableName, color: 'var(--color-subtle-on-dark)' },
        { tag: [t.string, t.special(t.brace)], color: '#fff' },
        { tag: t.number, color: 'var(--syntax-number)' },
        { tag: t.string, color: 'var(--syntax-selector)' },
        { tag: t.bool, color: 'var(--syntax-keyword)' },
        { tag: t.keyword, color: 'var(--syntax-keyword)' },
        { tag: t.operator, color: 'var(--syntax-operator)' },
    ],
})

export default class Juniper extends React.Component {
    state = {
        kernel: null,
        renderers: null,
        fromStorage: null,
        output: null,
        code: this.props.children,
    }

    log(logFunction) {
        if (this.props.debug) {
            logFunction()
        }
    }

    /**
     * Request a binder, e.g. from mybinder.org
     * @param {string} repo - Repository name in the format 'user/repo'.
     * @param {string} branch - The repository branch, e.g. 'master'.
     * @param {string} url - The binder reployment URL, including 'http(s)'.
     * @returns {Promise} - Resolved with Binder settings, rejected with Error.
     */
    requestBinder(repo, branch, url) {
        const binderUrl = `${url}/build/gh/${repo}/${branch}`
        this.log(() => console.info('building', { binderUrl }))
        return new Promise((resolve, reject) => {
            const es = new EventSource(binderUrl)
            es.onerror = (err) => {
                es.close()
                this.log(() => console.error('failed', err))
                reject(new Error(err))
            }
            let phase = null
            es.onmessage = ({ data }) => {
                const msg = JSON.parse(data)
                if (msg.phase && msg.phase !== phase) {
                    phase = msg.phase.toLowerCase()
                    this.log(() => console.info(phase === 'ready' ? 'server-ready' : phase))
                }
                if (msg.phase === 'failed') {
                    es.close()
                    reject(new Error(msg))
                } else if (msg.phase === 'ready') {
                    es.close()
                    const settings = {
                        baseUrl: msg.url,
                        wsUrl: `ws${msg.url.slice(4)}`,
                        token: msg.token,
                    }
                    resolve(settings)
                }
            }
        })
    }

    /**
     * Request kernel and estabish a server connection via the JupyerLab service
     * @param {object} settings - The server settings.
     * @returns {Promise} - A promise that's resolved with the kernel.
     */
    requestKernel(settings) {
        if (this.props.useStorage) {
            const timestamp = new Date().getTime() + this.props.storageExpire * 60 * 1000
            const json = JSON.stringify({ settings, timestamp })
            window.localStorage.setItem(this.props.storageKey, json)
        }
        const serverSettings = ServerConnection.makeSettings(settings)
        return Kernel.startNew({ type: this.props.kernelType, serverSettings }).then((kernel) => {
            this.log(() => console.info('ready'))
            return kernel
        })
    }

    /**
     * Get a kernel by requesting a binder or from localStorage / user settings
     * @returns {Promise}
     */
    getKernel() {
        if (this.props.useStorage) {
            const stored = window.localStorage.getItem(this.props.storageKey)
            if (stored) {
                this.setState({ fromStorage: true })
                const { settings, timestamp } = JSON.parse(stored)
                if (timestamp && new Date().getTime() < timestamp) {
                    return this.requestKernel(settings)
                }
                window.localStorage.removeItem(this.props.storageKey)
            }
        }
        if (this.props.useBinder) {
            return this.requestBinder(this.props.repo, this.props.branch, this.props.url).then(
                (settings) => this.requestKernel(settings)
            )
        }
        return this.requestKernel(this.props.serverSettings)
    }

    /**
     * Render the kernel response in a JupyterLab output area
     * @param {OutputArea} outputArea - The cell's output area.
     * @param {string} code - The code to execute.
     */
    async renderResponse(kernel) {
        if (this.state.code === null || this.state.code === '') {
            this.state.output = 'No code entered'
            return
        }

        const response = kernel.requestExecute({
            code: this.state.code,
        })

        this.state.output = this.props.msgLoading

        response.handleMsg = (message) => {
            if (message.content && message.content.name === 'stdout') {
                this.setState({
                    output: message.content.text,
                })
            }
        }
    }

    /**
     * Process request to execute the code
     * @param {OutputArea} - outputArea - The cell's output area.
     * @param {string} code - The code to execute.
     */
    runCode() {
        this.log(() => console.info('executing'))
        if (this.state.kernel) {
            if (this.props.isolateCells) {
                this.state.kernel
                    .restart()
                    .then(() => this.renderResponse(this.state.kernel))
                    .catch((err) => {
                        this.log(() => console.error('faileder', err))
                        this.setState({ kernel: null })
                        this.setState({ output: this.props.msgError })
                    })
                return
            }
            this.renderResponse(this.state.kernel)
            return
        }
        this.log(() => console.info('requesting kernel'))
        const url = this.props.url.split('//')[1]
        const action = !this.state.fromStorage ? 'Launching' : 'Reconnecting to'
        this.setState({ output: `${action} Docker container on ${url}...` })
        this.getKernel()
            .then((kernel) => {
                this.setState({ kernel })
                this.renderResponse(kernel)
            })
            .catch((err) => {
                this.log(() => console.error('failed', err))
                this.setState({ kernel: null })
                if (this.props.useStorage) {
                    this.setState({ fromStorage: false })
                    window.localStorage.removeItem(this.props.storageKey)
                }
                this.setState({ output: this.props.msgError })
            })
    }

    render() {
        return (
            <div className={this.props.classNames.cell}>
                {this.state.code && (
                    <CodeMirror
                        value={this.state.code}
                        extensions={[python()]}
                        theme={spacyTheme}
                        basicSetup={{
                            lineNumbers: false,
                            foldGutter: false,
                            highlightActiveLine: false,
                            highlightSelectionMatches: false,
                        }}
                        className={classes['juniper-input']}
                        onChange={(value) => {
                            this.setState({ code: value })
                        }}
                    />
                )}
                <button className={this.props.classNames.button} onClick={() => this.runCode()}>
                    {this.props.msgButton}
                </button>
                {this.state.output !== null && (
                    <pre
                        className={`${this.props.classNames.output} ${classes['juniper-input']} ${classes.wrap}`}
                    >
                        {this.state.output}
                    </pre>
                )}
            </div>
        )
    }
}

Juniper.defaultProps = {
    children: '',
    branch: 'master',
    url: 'https://mybinder.org',
    serverSettings: {},
    kernelType: 'python3',
    lang: 'python',
    theme: 'default',
    isolateCells: true,
    useBinder: true,
    storageKey: 'juniper',
    useStorage: true,
    storageExpire: 60,
    debug: false,
    msgButton: 'run',
    msgLoading: 'Loading...',
    msgError: 'Connecting failed. Please reload and try again.',
    classNames: {
        cell: 'juniper-cell',
        input: 'juniper-input',
        button: 'juniper-button',
        output: 'juniper-output',
    },
}

Juniper.propTypes = {
    children: PropTypes.string,
    repo: PropTypes.string.isRequired,
    branch: PropTypes.string,
    url: PropTypes.string,
    serverSettings: PropTypes.object,
    kernelType: PropTypes.string,
    lang: PropTypes.string,
    theme: PropTypes.string,
    isolateCells: PropTypes.bool,
    useBinder: PropTypes.bool,
    useStorage: PropTypes.bool,
    storageExpire: PropTypes.number,
    msgButton: PropTypes.string,
    msgLoading: PropTypes.string,
    msgError: PropTypes.string,
    classNames: PropTypes.shape({
        cell: PropTypes.string,
        input: PropTypes.string,
        button: PropTypes.string,
        output: PropTypes.string,
    }),
}
