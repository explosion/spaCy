//- 💫 MAIN JAVASCRIPT
//- Note: Will be compiled using Babel before deployment.

'use strict'

const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);


class ProgressBar {
    /**
     * Animated reading progress bar.
     * @param {String} selector – CSS selector of progress bar element.
     */
    constructor(selector) {
        this.el = $(selector);
        this.scrollY = 0;
        this.sizes = this.updateSizes();
        this.el.setAttribute('max', 100);
        this.init();
    }

    init() {
        window.addEventListener('scroll', () => {
            this.scrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0);
            requestAnimationFrame(this.update.bind(this));
        }, false);
        window.addEventListener('resize', () => {
            this.sizes = this.updateSizes();
            requestAnimationFrame(this.update.bind(this));
        })
    }

    update() {
        const offset = 100 - ((this.sizes.height - this.scrollY - this.sizes.vh) / this.sizes.height * 100);
        this.el.setAttribute('value', (this.scrollY == 0) ? 0 : offset || 0);
    }

    updateSizes() {
        const body = document.body;
        const html = document.documentElement;
        return {
            height: Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight),
            vh: Math.max(html.clientHeight, window.innerHeight || 0)
        }
    }
}


class SectionHighlighter {
    /**
     * Hightlight section in viewport in sidebar, using in-view library.
     * @param {String} sectionAttr - Data attribute of sections.
     * @param {String} navAttr - Data attribute of navigation items.
     * @param {String} activeClass – Class name of active element.
     */
    constructor(sectionAttr, navAttr, activeClass = 'is-active') {
        this.sections = [...$$(`[${navAttr}]`)];
        this.navAttr = navAttr;
        this.sectionAttr = sectionAttr;
        this.activeClass = activeClass;
        inView(`[${sectionAttr}]`).on('enter', this.highlightSection.bind(this));
    }

    highlightSection(section) {
        const id = section.getAttribute(this.sectionAttr);
        const el = $(`[${this.navAttr}="${id}"]`);
        if (el) {
            this.sections.forEach(el => el.classList.remove(this.activeClass));
            el.classList.add(this.activeClass);
        }
    }
}


class Templater {
    /**
     * Mini templating engine based on data attributes. Selects elements based
     * on a data-tpl and data-tpl-key attribute and can set textContent
     * and innterHtml.
     *
     * @param {String} templateId - Template section, e.g. value of data-tpl.
     */
    constructor(templateId) {
        this.templateId = templateId;
    }

    get(key) {
        return $(`[data-tpl="${this.templateId}"][data-tpl-key="${key}"]`);
    }

    fill(key, value, html = false) {
        const el = this.get(key);
        if (html) el.innerHTML = value || '';
        else el.textContent = value || '';
        return el;
    }
}


class ModelLoader {
    /**
     * Load model meta from GitHub and update model details on site. Uses the
     * Templater mini template engine to update DOM.
     *
     * @param {String} repo - Path tp GitHub repository containing releases.
     * @param {Array} models - List of model IDs, e.g. "en_core_web_sm".
     * @param {Object} licenses - License IDs mapped to URLs.
     * @param {Object} accKeys - Available accuracy keys mapped to display labels.
     */
    constructor(repo, models = [], licenses = {}, accKeys = {}) {
        this.url = `https://raw.githubusercontent.com/${repo}/master`;
        this.repo = `https://github.com/${repo}`;
        this.modelIds = models;
        this.licenses = licenses;
        this.accKeys = accKeys;
        this.chartColor = '#09a3d5';
        this.chartOptions = {
            type: 'bar',
            options: { responsive: true, scales: {
                yAxes: [{ label: 'Accuracy', ticks: { suggestedMin: 70 }}],
                xAxes: [{ barPercentage: 0.425 }]
            }}
        }
        Chart.defaults.global.legend.position = 'bottom';
        Chart.defaults.global.defaultFontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'";
        this.init();
    }

    init() {
        this.modelIds.forEach(modelId =>
            new Templater(modelId).get('table').setAttribute('data-loading', ''));
        fetch(`${this.url}/compatibility.json`)
            .then(res => this.handleResponse(res))
            .then(json => json.ok ? this.getModels(json['spacy']) : this.modelIds.forEach(modelId => this.showError(modelId)))
    }

    handleResponse(res) {
        if (res.ok) return res.json().then(json => Object.assign({}, json, { ok: res.ok }))
        else return ({ ok: res.ok })
    }

    getModels(compat) {
        this.compat = compat;
        for (let modelId of this.modelIds) {
            const version = this.getLatestVersion(modelId, compat);
            if (!version) {
                this.showError(modelId); return;
            }
            fetch(`${this.url}/meta/${modelId}-${version}.json`)
                .then(res => this.handleResponse(res))
                .then(json => json.ok ? this.render(json) : this.showError(modelId))
        }
        // make sure scroll positions for progress bar etc. are recalculated
        window.dispatchEvent(new Event('resize'));
    }

    showError(modelId) {
        const template = new Templater(modelId);
        template.get('table').removeAttribute('data-loading');
        template.get('error').style.display = 'block';
        for (let key of ['sources', 'pipeline', 'author', 'license']) {
            template.get(key).parentElement.parentElement.style.display = 'none';
        }
    }

    /**
     * Update model details in tables. Currently quite hacky :(
     */
    render({ lang, name, version, sources, pipeline, url, author, license, accuracy, size, description, notes }) {
        const modelId = `${lang}_${name}`;
        const model = `${modelId}-${version}`;
        const template = new Templater(modelId);

        const getSources = s => (s instanceof Array) ? s.join(', ') : s;
        const getPipeline = p => p.map(comp => `<code>${comp}</code>`).join(', ');
        const getLink = (t, l) => `<a href="${l}" target="_blank">${t}</a>`;

        const keys = { version, size, description, notes }
        Object.keys(keys).forEach(key => template.fill(key, keys[key]));

        if (sources) template.fill('sources', getSources(sources));
        if (pipeline && pipeline.length) template.fill('pipeline', getPipeline(pipeline), true);
        else template.get('pipeline').parentElement.parentElement.style.display = 'none';

        if (author) template.fill('author', url ? getLink(author, url) : author, true);
        if (license) template.fill('license', this.licenses[license] ? getLink(license, this.licenses[license]) : license, true);

        template.get('download').setAttribute('href', `${this.repo}/releases/tag/${model}`);
        if (accuracy) this.renderAccuracy(template, accuracy, modelId);
        this.renderCompat(template, modelId);
        template.get('table').removeAttribute('data-loading');
    }

    renderCompat(template, modelId) {
        template.get('compat-wrapper').style.display = 'table-row';
        const options = Object.keys(this.compat).map(v => `<option value="${v}">v${v}</option>`).join('');
        template
            .fill('compat', '<option selected disabled>spaCy version</option>' + options, true)
            .addEventListener('change', ev => {
                const result = this.compat[ev.target.value][modelId];
                if (result) template.fill('compat-versions', `<code>${modelId}-${result[0]}</code>`, true);
                else template.fill('compat-versions', '');
            });
    }

    renderAccuracy(template, accuracy, modelId, compare=false) {
        template.get('accuracy-wrapper').style.display = 'block';
        const metaKeys = Object.keys(this.accKeys).map(k => accuracy[k] ? k : false).filter(k => k);
        for (let key of metaKeys) {
            template.fill(key, accuracy[key].toFixed(2)).parentElement.style.display = 'table-row';
        }

        this.chartOptions.options.legend = { display: compare }
        new Chart(`chart_${modelId}`, Object.assign({}, this.chartOptions, { data: {
            datasets: [{
                label: modelId,
                data: metaKeys.map(key => accuracy[key].toFixed(2)),
                backgroundColor: this.chartColor
            }],
            labels: metaKeys.map(key => this.accKeys[key])
        }}))
    }

    getLatestVersion(model, compat = {}) {
        for (let spacy_v of Object.keys(compat)) {
            const models = compat[spacy_v];
            if (models[model]) return models[model][0];
        }
    }
}


class Changelog {
    /**
     * Fetch and render changelog from GitHub. Clones a template node (table row)
     * to avoid doubling templating markup in JavaScript.
     *
     * @param {String} user - GitHub username.
     * @param {String} repo - Repository to fetch releases from.
     */
    constructor(user, repo) {
        this.url = `https://api.github.com/repos/${user}/${repo}/releases`;
        this.template = new Templater('changelog');
        fetch(this.url)
            .then(res => this.handleResponse(res))
            .then(json => json.ok ? this.render(json) : false)
    }

    /**
     * Get template section from template row. Slightly hacky, but does make sense.
     */
    $(item, id) {
        return item.querySelector(`[data-changelog="${id}"]`);
    }

    handleResponse(res) {
        if (res.ok) return res.json().then(json => Object.assign({}, json, { ok: res.ok }))
        else return ({ ok: res.ok })
    }

    render(json) {
        this.template.get('error').style.display = 'none';
        this.template.get('table').style.display = 'block';
        this.row = this.template.get('item');
        this.releases = this.template.get('releases');
        this.prereleases = this.template.get('prereleases');
        Object.values(json)
            .filter(release => release.name)
            .forEach(release => this.renderRelease(release));
        this.row.remove();
        // make sure scroll positions for progress bar etc. are recalculated
        window.dispatchEvent(new Event('resize'));
    }

    /**
     * Clone the template row and populate with content from API response.
     * https://developer.github.com/v3/repos/releases/#list-releases-for-a-repository
     *
     * @param {String} name - Release title.
     * @param {String} tag (tag_name) - Release tag.
     * @param {String} url (html_url) - URL to the release page on GitHub.
     * @param {String} date (published_at) - Timestamp of release publication.
     * @param {Boolean} pre (prerelease) - Whether the release is a prerelease.
     */
    renderRelease({ name, tag_name: tag, html_url: url, published_at: date, prerelease: pre }) {
        const container = pre ? this.prereleases : this.releases;
        const row = this.row.cloneNode(true);
        this.$(row, 'date').textContent = date.split('T')[0];
        this.$(row, 'tag').innerHTML = `<a href="${url}" target="_blank"><code>${tag}</code></a>`;
        this.$(row, 'title').textContent = (name.split(': ').length == 2) ? name.split(': ')[1] : name;
        container.appendChild(row);
    }
}


class GitHubEmbed {
    /**
     * Embed code from GitHub repositories, similar to Gist embeds. Fetches the
     * raw text and places it inside element.
     * Usage: <pre><code data-gh-embed="spacy/master/examples/x.py"></code><pre>
     *
     * @param {String} user - GitHub user or organization.
     * @param {String} attr - Data attribute used to select containers. Attribute
     *                        value should be path to file relative to user.
     */
    constructor(user, attr) {
        this.url = `https://raw.githubusercontent.com/${user}`;
        this.attr = attr;
        this.error = `\nCan't fetch code example from GitHub :(\n\nPlease use the link below to view the example. If you've come across\na broken link, we always appreciate a pull request to the repository,\nor a report on the issue tracker. Thanks!`;
        [...$$(`[${this.attr}]`)].forEach(el => this.embed(el));
    }

    embed(el) {
        el.parentElement.setAttribute('data-loading', '');
        fetch(`${this.url}/${el.getAttribute(this.attr)}`)
            .then(res => res.text().then(text => ({ text, ok: res.ok })))
            .then(({ text, ok }) => {
                el.textContent = ok ? text : this.error;
                if (ok && window.Prism) Prism.highlightElement(el);
            })
        el.parentElement.removeAttribute('data-loading');
    }
}
