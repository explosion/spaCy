'use strict';

import { Templater, handleResponse, convertNumber, abbrNumber } from './util.js';

/**
 * Chart.js defaults
 */
const CHART_COLORS = { model1: '#09a3d5', model2: '#066B8C' };
const CHART_FONTS = {
    legend: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',
    ticks: 'Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
};

/**
 * Formatters for model details.
 * @property {function} author – Format model author with optional link.
 * @property {function} license - Format model license with optional link.
 * @property {function} sources - Format training data sources (list or string).
 * @property {function} pipeline - Format list of pipeline components.
 * @property {function} vectors - Format vector data (entries and dimensions).
 * @property {function} version - Format model version number.
 */
const formats = {
    author: (author, url) => url ? `<a href="${url}" target="_blank">${author}</a>` : author,
    license: (license, url) => url ? `<a href="${url}" target="_blank">${license}</a>` : license,
    sources: sources => (sources instanceof Array) ? sources.join(', ') : sources,
    pipeline: pipes => (pipes && pipes.length) ? pipes.map(p => `<code>${p}</code>`).join(', ') : '-',
    vectors: vec => formatVectors(vec),
    version: version => `<code>v${version}</code>`
};

/**
 * Format word vectors data depending on contents.
 * @property {Object} data - The vectors object from the model's meta.json.
 */
const formatVectors = data => {
    if (!data) return 'n/a';
    if (Object.values(data).every(n => n == 0)) return 'context vectors only';
    const { keys, vectors: vecs, width } = data;
    return `${abbrNumber(keys)} keys, ${abbrNumber(vecs)} unique vectors (${width} dimensions)`;
}


/**
 * Find the latest version of a model in a compatibility table.
 * @param {string} model - The model name.
 * @param {Object} compat - Compatibility table, keyed by spaCy version.
 */
const getLatestVersion = (model, compat = {}) => {
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
        tpl.get('error').hidden = false;
        for (let key of ['sources', 'pipeline', 'vecs', 'author', 'license']) {
            tpl.get(key).parentElement.parentElement.hidden = true;
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
        tpl.get('error').hidden = true;
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
        if (vectors) tpl.fill('vecs', formats.vectors(vectors));
        else tpl.get('vecs').parentElement.parentElement.hidden = true;
        if (pipeline && pipeline.length) tpl.fill('pipeline', formats.pipeline(pipeline), true);
        else tpl.get('pipeline').parentElement.parentElement.hidden = true;
    }

    renderBenchmarks(tpl, accuracy = {}, speed = {}) {
        if (!accuracy && !speed) return;
        this.renderTable(tpl, 'parser', accuracy, val => val.toFixed(2));
        this.renderTable(tpl, 'ner', accuracy, val => val.toFixed(2));
        tpl.get('benchmarks').hidden = false;
    }

    renderTable(tpl, id, benchmarks, converter = val => val) {
        if (!this.benchKeys[id] || !Object.keys(this.benchKeys[id]).some(key => benchmarks[key])) return;
        for (let key of Object.keys(this.benchKeys[id])) {
            if (benchmarks[key]) tpl
                .fill(key, convertNumber(converter(benchmarks[key])))
                .parentElement.hidden = false;
        }
        tpl.get(id).hidden = false;
    }

    renderCompat(tpl, modelId) {
        tpl.get('compat-wrapper').hidden = false;
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

export class ModelComparer {
    /**
     * Compare to model meta files and render chart and comparison table.
     * @param {string} repo - Path tp GitHub repository containing releases.
     * @param {Object} licenses - License IDs mapped to URLs.
     * @param {Object} benchmarkKeys - Objects of available keys by type, e.g.
     *                                 'parser', 'ner', 'speed', mapped to labels.
     * @param {Object} languages - Available languages, ID mapped to name.
     * @param {Object} defaultModels - Models to compare on load, 'model1' and
     *                                 'model2' mapped to model names.
     */
    constructor(repo, licenses = {}, benchmarkKeys = {}, languages = {}, labels = {}, defaultModels) {
        this.url = `https://raw.githubusercontent.com/${repo}/master`;
        this.repo = `https://github.com/${repo}`;
        this.tpl = new Templater('compare');
        this.benchKeys = benchmarkKeys;
        this.licenses = licenses;
        this.languages = languages;
        this.labels = labels;
        this.models = {};
        this.colors = CHART_COLORS;
        this.fonts = CHART_FONTS;
        this.defaultModels = defaultModels;
        this.tpl.get('result').hidden = false;
        this.tpl.get('error').hidden = true;
        this.fetchCompat()
            .then(compat => this.init(compat))
            .catch(this.showError.bind(this))
    }

    init(compat) {
        this.compat = compat;
        const selectA = this.tpl.get('model1');
        const selectB = this.tpl.get('model2');
        selectA.addEventListener('change', this.onSelect.bind(this));
        selectB.addEventListener('change', this.onSelect.bind(this));
        this.chart = new Chart('chart_compare_accuracy', { type: 'bar', options: {
            responsive: true,
            legend: { position: 'bottom', labels: { fontFamily: this.fonts.legend, fontSize: 13 }},
            scales: {
                yAxes: [{ label: 'Accuracy', ticks: { min: 70, fontFamily: this.fonts.ticks }}],
                xAxes: [{ barPercentage: 0.75, ticks: { fontFamily: this.fonts.ticks }}]
            }
        }});
        if (this.defaultModels) {
            selectA.value = this.defaultModels.model1;
            selectB.value = this.defaultModels.model2;
            this.getModels(this.defaultModels);
        }
    }

    fetchCompat() {
        return new Promise((resolve, reject) =>
            fetch(`${this.url}/compatibility.json`)
                .then(res => handleResponse(res))
                .then(json => json.ok ? resolve(json.spacy) : reject()))
    }

    fetchModel(name) {
        const version = getLatestVersion(name, this.compat);
        const modelName = `${name}-${version}`;
        return new Promise((resolve, reject) => {
            if (!version) reject();
            // resolve immediately if model already loaded, e.g. in this.models
            else if (this.models[name]) resolve(this.models[name]);
            else fetch(`${this.url}/meta/${modelName}.json`)
                .then(res => handleResponse(res))
                .then(json => json.ok ? resolve(this.saveModel(name, json)) : reject())
        })
    }

    /**
     * "Save" meta to this.models so it only has to be fetched from GitHub once.
     * @param {string} name - The model name.
     * @param {Object} data - The model meta data.
     */
    saveModel(name, data) {
        this.models[name] = data;
        return data;
    }

    showError(err) {
        console.error(err || 'Error');
        this.tpl.get('result').hidden = true;
        this.tpl.get('error').hidden = false;
    }

    onSelect(ev) {
        const modelId = ev.target.value;
        const otherId = (ev.target.id == 'model1') ? 'model2' : 'model1';
        const otherVal = this.tpl.get(otherId);
        const otherModel = otherVal.options[otherVal.selectedIndex].value;
        if (otherModel != '') this.getModels({
            [ev.target.id]: modelId,
            [otherId]: otherModel
        })
    }

    getModels({ model1, model2 }) {
        this.tpl.get('result').setAttribute('data-loading', '');
        this.fetchModel(model1)
            .then(data1 => this.fetchModel(model2)
                .then(data2 => this.render({ model1: data1, model2: data2 })))
                .catch(this.showError.bind(this))
    }

    /**
     * Render two models, and populate the chart and table. Currently quite hacky :(
     * @param {Object} models - The models to render.
     * @param {Object} models.model1 - The first model (via first <select>).
     * @param {Object} models.model2 - The second model (via second <select>).
     */
    render({ model1, model2 }) {
        const accKeys = Object.assign({}, this.benchKeys.parser, this.benchKeys.ner);
        const allKeys = [...Object.keys(model1.accuracy || []), ...Object.keys(model2.accuracy || [])];
        const metaKeys = Object.keys(accKeys).filter(k => allKeys.includes(k));
        const labels = metaKeys.map(key => accKeys[key]);
        const datasets = [model1, model2]
            .map(({ lang, name, version, accuracy = {} }, i) => ({
                label: `${lang}_${name}-${version}`,
                backgroundColor: this.colors[`model${i + 1}`],
                data: metaKeys.map(key => (accuracy[key] || 0).toFixed(2))
            }));
        this.chart.data = { labels, datasets };
        this.chart.update();
        [model1, model2].forEach((model, i) => this.renderTable(metaKeys, i + 1, model));
        this.tpl.get('result').removeAttribute('data-loading');
        this.tpl.get('error').hidden = true;
        this.tpl.get('result').hidden = false;
    }

    renderTable(metaKeys, i, { lang, name, version, size, description,
        notes, author, url, license, sources, vectors, pipeline, accuracy = {},
        speed = {}}) {
        const type = name.split('_')[0];  // extract type from model name
        const genre = name.split('_')[1];  // extract genre from model name
        this.tpl.fill(`table-head${i}`, `${lang}_${name}`);
        this.tpl.get(`link${i}`).setAttribute('href', `/models/${lang}#${lang}_${name}`);
        this.tpl.fill(`download${i}`, `python -m spacy download ${lang}_${name}\n`);
        this.tpl.fill(`lang${i}`, this.languages[lang] || lang);
        this.tpl.fill(`type${i}`, this.labels[type] || type);
        this.tpl.fill(`genre${i}`, this.labels[genre] || genre);
        this.tpl.fill(`version${i}`, formats.version(version), true);
        this.tpl.fill(`size${i}`, size);
        this.tpl.fill(`desc${i}`, description || 'n/a');
        this.tpl.fill(`pipeline${i}`, formats.pipeline(pipeline), true);
        this.tpl.fill(`vecs${i}`, formats.vectors(vectors));
        this.tpl.fill(`sources${i}`, formats.sources(sources));
        this.tpl.fill(`author${i}`, formats.author(author, url), true);
        this.tpl.fill(`license${i}`, formats.license(license, this.licenses[license]), true);
        // check if model accuracy or speed includes one of the pre-set keys
        const allKeys = [].concat(...Object.entries(this.benchKeys).map(([_, v]) => Object.keys(v)));
        for (let key of allKeys) {
            if (accuracy[key]) this.tpl.fill(`${key}${i}`, accuracy[key].toFixed(2))
            else this.tpl.fill(`${key}${i}`, 'n/a')
        }
    }
}
