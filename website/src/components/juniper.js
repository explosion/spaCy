import React from 'react'
import PropTypes from 'prop-types'
import CodeMirror from 'codemirror'
import python from 'codemirror/mode/python/python' // eslint-disable-line no-unused-vars
import { Widget } from '@phosphor/widgets'
import { Kernel, ServerConnection } from '@jupyterlab/services'
import { OutputArea, OutputAreaModel } from '@jupyterlab/outputarea'
import { RenderMimeRegistry, standardRendererFactories } from '@jupyterlab/rendermime'
import { window } from 'browser-monads'

export default class Juniper extends React.Component {
    outputRef = null
    inputRef = null
    state = { kernel: null, renderers: null, fromStorage: null }

    componentDidMount() {
        const renderers = standardRendererFactories.filter(factory =>
            factory.mimeTypes.includes('text/latex') ? window.MathJax : true
        )

        const outputArea = new OutputArea({
            model: new OutputAreaModel({ trusted: true }),
            rendermime: new RenderMimeRegistry({ initialFactories: renderers }),
        })

        const cm = new CodeMirror(this.inputRef, {
            value: this.props.children.trim(),
            mode: this.props.lang,
            theme: this.props.theme,
        })
        const runCode = () => this.execute(outputArea, cm.getValue())
        cm.setOption('extraKeys', { 'Shift-Enter': runCode })
        Widget.attach(outputArea, this.outputRef)
        this.setState({ runCode })
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
            es.onerror = err => {
                es.close()
                this.log(() => console.error('failed'))
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
        return Kernel.startNew({ type: this.props.kernelType, serverSettings }).then(kernel => {
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
                settings => this.requestKernel(settings)
            )
        }
        return this.requestKernel(this.props.serverSettings)
    }

    /**
     * Render the kernel response in a JupyterLab output area
     * @param {OutputArea} outputArea - The cell's output area.
     * @param {string} code - The code to execute.
     */
    renderResponse(outputArea, code) {
        outputArea.future = this.state.kernel.requestExecute({ code })
        outputArea.model.add({
            output_type: 'stream',
            name: 'loading',
            text: this.props.msgLoading,
        })
        outputArea.model.clear(true)
    }

    /**
     * Process request to execute the code
     * @param {OutputArea} - outputArea - The cell's output area.
     * @param {string} code - The code to execute.
     */
    execute(outputArea, code) {
        this.log(() => console.info('executing'))
        if (this.state.kernel) {
            if (this.props.isolateCells) {
                this.state.kernel
                    .restart()
                    .then(() => this.renderResponse(outputArea, code))
                    .catch(() => {
                        this.log(() => console.error('failed'))
                        this.setState({ kernel: null })
                        outputArea.model.clear()
                        outputArea.model.add({
                            output_type: 'stream',
                            name: 'failure',
                            text: this.props.msgError,
                        })
                    })
                return
            }
            this.renderResponse(outputArea, code)
            return
        }
        this.log(() => console.info('requesting kernel'))
        const url = this.props.url.split('//')[1]
        const action = !this.state.fromStorage ? 'Launching' : 'Reconnecting to'
        outputArea.model.clear()
        outputArea.model.add({
            output_type: 'stream',
            name: 'stdout',
            text: `${action} Docker container on ${url}...`,
        })
        new Promise((resolve, reject) =>
            this.getKernel()
                .then(resolve)
                .catch(reject)
        )
            .then(kernel => {
                this.setState({ kernel })
                this.renderResponse(outputArea, code)
            })
            .catch(() => {
                this.log(() => console.error('failed'))
                this.setState({ kernel: null })
                if (this.props.useStorage) {
                    this.setState({ fromStorage: false })
                    window.localStorage.removeItem(this.props.storageKey)
                }
                outputArea.model.clear()
                outputArea.model.add({
                    output_type: 'stream',
                    name: 'failure',
                    text: this.props.msgError,
                })
            })
    }

    render() {
        return (
            <div className={this.props.classNames.cell}>
                <div
                    className={this.props.classNames.input}
                    ref={x => {
                        this.inputRef = x
                    }}
                />
                <button className={this.props.classNames.button} onClick={this.state.runCode}>
                    {this.props.msgButton}
                </button>
                <div
                    ref={x => {
                        this.outputRef = x
                    }}
                    className={this.props.classNames.output}
                />
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
