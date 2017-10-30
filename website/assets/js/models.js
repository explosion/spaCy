'use strict';

import { Templater, handleResponse, convertNumber } from './util.js';

/**
 * Chart.js defaults
 */
Chart.defaults.global.legend.position = 'bottom';
Chart.defaults.global.defaultFontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'";
const CHART_COLORS = { model1: '#09a3d5', model2: '#066B8C' };

/**
 * Formatters for model details.
 * @property {function} author – Format model author with optional link.
 * @property {function} license - Format model license with optional link.
 * @property {function} sources - Format training data sources (list or string).
 * @property {function} pipeline - Format list of pipeline components.
 * @property {function} vectors - Format vector data (entries and dimensions).
 * @property {function} version - Format model version number.
 */
export const formats = {
    author: (author, url) => url ? `<a href="${url}" target="_blank">${author}</a>` : author,
    license: (license, url) => url ? `<a href="${url}" target="_blank">${license}</a>` : license,
    sources: sources => (sources instanceof Array) ? sources.join(', ') : sources,
    pipeline: pipes => (pipes && pipes.length) ? pipes.map(p => `<code>${p}</code>`).join(', ') : '-',
    vectors: vec => vec ? `${convertNumber(vec.entries)} (${vec.width} dimensions)` : 'n/a',
    version: version => `<code>v${version}</code>`
};

/**
 * Find the latest version of a model in a compatibility table.
 * @param {string} model - The model name.
 * @param {Object} compat - Compatibility table, keyed by spaCy version.
 */
export const getLatestVersion = (model, compat = {}) => {
    for (let [spacy_v, models] of Object.entries(compat)) {
        if (models[model]) return models[model][0];
    }
};

export class ModelLoader {
    /**
     * Load model meta from GitHub and update model details on site. Uses the
     * Templater mini template engine to update DOM.
     * @param {string} repo - Path tp GitHub repository containing releases.
     * @param {Array} models - List of model IDs, e.g. "en_core_web_sm".
     * @param {Object} licenses - License IDs mapped to URLs.
     * @param {Object} benchmarkKeys - Objects of available keys by type, e.g.
     *                                 'parser', 'ner', 'speed', mapped to labels.
     */
    constructor(repo, models = [], licenses = {}, benchmarkKeys = {}) {
        this.url = `https://raw.githubusercontent.com/${repo}/master`;
        this.repo = `https://github.com/${repo}`;
        this.modelIds = models;
        this.licenses = licenses;
        this.benchKeys = benchmarkKeys;
        this.init();
    }

    init() {
        this.modelIds.forEach(modelId =>
            new Templater(modelId).get('table').setAttribute('data-loading', ''));
        this.fetch(`${this.url}/compatibility.json`)
            .then(json => this.getModels(json.spacy))
            .catch(_ => this.modelIds.forEach(modelId => this.showError(modelId)));
        // make sure scroll positions for progress bar etc. are recalculated
        window.dispatchEvent(new Event('resize'));
    }

    fetch(url) {
        return new Promise((resolve, reject) =>
            fetch(url).then(res => handleResponse(res))
                .then(json => json.ok ? resolve(json) : reject()))
    }

    getModels(compat) {
        this.compat = compat;
        for (let modelId of this.modelIds) {
            const version = getLatestVersion(modelId, compat);
            if (version) this.fetch(`${this.url}/meta/${modelId}-${version}.json`)
                .then(json => this.render(json))
                .catch(_ => this.showError(modelId))
            else this.showError(modelId);
        }
    }

    showError(modelId) {
        const tpl = new Templater(modelId);
        tpl.get('table').removeAttribute('data-loading');
        tpl.get('error').style.display = 'block';
        for (let key of ['sources', 'pipeline', 'vectors', 'author', 'license']) {
            tpl.get(key).parentElement.parentElement.style.display = 'none';
        }
    }

    /**
     * Update model details in tables. Currently quite hacky :(
     */
    render(data) {
        const modelId = `${data.lang}_${data.name}`;
        const model = `${modelId}-${data.version}`;
        const tpl = new Templater(modelId);
        this.renderDetails(tpl, data)
        this.renderBenchmarks(tpl, data.accuracy, data.speed);
        this.renderCompat(tpl, modelId);
        tpl.get('download').setAttribute('href', `${this.repo}/releases/tag/${model}`);
        tpl.get('table').removeAttribute('data-loading');
    }

    renderDetails(tpl, { version, size, description, notes, author, url,
        license, sources, vectors, pipeline }) {
        const basics = { version, size, description, notes }
        for (let [key, value] of Object.entries(basics)) {
            if (value) tpl.fill(key, value);
        }
        if (author) tpl.fill('author', formats.author(author, url), true);
        if (license) tpl.fill('license', formats.license(license, this.licenses[license]), true);
        if (sources) tpl.fill('sources', formats.sources(sources));
        if (vectors) tpl.fill('vectors', formats.vectors(vectors));
        else tpl.get('vectors').parentElement.parentElement.style.display = 'none';
        if (pipeline && pipeline.length) tpl.fill('pipeline', formats.pipeline(pipeline), true);
        else tpl.get('pipeline').parentElement.parentElement.style.display = 'none';
    }

    renderBenchmarks(tpl, accuracy = {}, speed = {}) {
        if (!accuracy && !speed) return;
        this.renderTable(tpl, 'parser', accuracy, val => val.toFixed(2));
        this.renderTable(tpl, 'ner', accuracy, val => val.toFixed(2));
        this.renderTable(tpl, 'speed', speed, Math.round);
        tpl.get('benchmarks').style.display = 'block';
    }

    renderTable(tpl, id, benchmarks, converter = val => val) {
        if (!this.benchKeys[id] || !Object.keys(this.benchKeys[id]).some(key => benchmarks[key])) return;
        for (let key of Object.keys(this.benchKeys[id])) {
            if (benchmarks[key]) tpl
                .fill(key, convertNumber(converter(benchmarks[key])))
                .parentElement.style.display = 'table-row';
        }
        tpl.get(id).style.display = 'block';
    }

    renderCompat(tpl, modelId) {
        tpl.get('compat-wrapper').style.display = 'table-row';
        const header = '<option selected disabled>spaCy version</option>';
        const options = Object.keys(this.compat)
            .map(v => `<option value="${v}">v${v}</option>`)
            .join('');
        tpl
            .fill('compat', header + options, true)
            .addEventListener('change', ({ target: { value }}) =>
                tpl.fill('compat-versions', this.getCompat(value, modelId), true))
    }

    getCompat(version, model) {
        const res = this.compat[version][model];
        return res ? `<code>${model}-${res[0]}</code>` : '<em>not compatible</em>';
    }
}

