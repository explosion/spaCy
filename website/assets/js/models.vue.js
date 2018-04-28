/**
 * Initialise model overviews
 * @param {string} repo - Repository to load from, in the format user/repo.
 */
export default function(repo) {
    const LICENSES = {
        'CC BY 4.0':       'https://creativecommons.org/licenses/by/4.0/',
        'CC BY-SA':        'https://creativecommons.org/licenses/by-sa/3.0/',
        'CC BY-SA 3.0':    'https://creativecommons.org/licenses/by-sa/3.0/',
        'CC BY-SA 4.0':    'https://creativecommons.org/licenses/by-sa/4.0/',
        'CC BY-NC':        'https://creativecommons.org/licenses/by-nc/3.0/',
        'CC BY-NC 3.0':    'https://creativecommons.org/licenses/by-nc/3.0/',
        'CC-BY-NC-SA 3.0': 'https://creativecommons.org/licenses/by-nc-sa/3.0/',
        'GPL':             'https://www.gnu.org/licenses/gpl.html',
        'LGPL':            'https://www.gnu.org/licenses/lgpl.html',
        'MIT':             'https://opensource.org/licenses/MIT'
    };
    const URL = `https://raw.githubusercontent.com/${repo}/master`;
    const models = [...document.querySelectorAll('[data-vue]')]
        .map(el => el.getAttribute('data-vue'));

    document.addEventListener('DOMContentLoaded', ev => {
        fetch(`${URL}/compatibility.json`)
            .then(res => res.json())
            .then(json => models.forEach(modelId => new Vue({
                el: `[data-vue="${modelId}"]`,
                data: {
                    repo: `https://github.com/${repo}`,
                    compat: json.spacy,
                    loading: false,
                    error: false,
                    id: modelId,
                    version: 'n/a',
                    notes: null,
                    sizeFull: null,
                    pipeline: null,
                    releaseUrl: null,
                    description: null,
                    license: null,
                    author: null,
                    url: null,
                    vectors: null,
                    sources: null,
                    uas: null,
                    las: null,
                    tags_acc: null,
                    ents_f: null,
                    ents_p: null,
                    ents_r: null,
                    modelLicenses: LICENSES,
                    spacyVersion: Object.keys(json.spacy)[0]
                },
                computed: {
                    compatVersion() {
                        const res = this.compat[this.spacyVersion][this.id];
                        return res ? `${this.id}-${res[0]}` : false;
                    },
                    orderedCompat() {
                        return Object.keys(this.compat)
                            .filter(v => !v.includes('a') && !v.includes('dev') && !v.includes('rc'));
                    },
                    hasAccuracy() {
                        return this.uas || this.las || this.tags_acc || this.ents_f || this.ents_p || this.ents_r;
                    }
                },
                beforeMount() {
                    const version = this.$_getLatestVersion(this.id);
                    if (version) {
                        this.loading = true;
                        fetch(`${URL}/meta/${this.id}-${version}.json`)
                            .then(res => res.json())
                            .then(json => this.$_updateData(json))
                            .catch(err => { this.error = true });
                    }
                },
                updated() {
                    window.dispatchEvent(new Event('resize'));  // scroll position for progress
                },
                methods: {
                    $_updateData(data) {
                        const fullName = `${data.lang}_${data.name}-${data.version}`;
                        this.version = data.version;
                        this.releaseUrl = `${this.repo}/releases/tag/${fullName}`;
                        this.sizeFull = data.size;
                        this.pipeline = data.pipeline;
                        this.notes = data.notes;
                        this.description = data.description;
                        this.vectors = this.$_formatVectors(data.vectors);
                        this.sources = data.sources;
                        this.author = data.author;
                        this.url = data.url;
                        this.license = data.license;
                        const accuracy = data.accuracy || {};
                        for (let key of Object.keys(accuracy)) {
                            this[key] = accuracy[key].toFixed(2);
                        }
                        this.loading = false;
                    },

                    $_getLatestVersion(modelId) {
                        for (let [spacy_v, models] of Object.entries(this.compat)) {
                            if (models[modelId]) {
                                return models[modelId][0];
                            }
                        }
                    },

                    $_formatVectors(data) {
                        if (!data) {
                            return 'n/a';
                        }
                        if (Object.values(data).every(n => n == 0)) {
                            return 'context vectors only';
                        }
                        const { keys, vectors, width } = data;
                        const nKeys = this.$_abbrNum(keys);
                        const nVectors = this.$_abbrNum(vectors);
                        return `${nKeys} keys, ${nVectors} unique vectors (${width} dimensions)`;
                    },

                    /**
                     * Abbreviate a number, e.g. 14249930 --> 14.25m.
                     * @param {number|string} num - The number to convert.
                     * @param {number} fixed - Number of decimals.
                     */
                    $_abbrNum: function(num = 0, fixed = 1) {
                        const suffixes = ['', 'k', 'm', 'b', 't'];
                        if (num === null || num === 0) return 0;
                        const b = num.toPrecision(2).split('e');
                        const k = (b.length === 1) ? 0 : Math.floor(Math.min(b[1].slice(1), 14) / 3);
                        const n = (k < 1) ? num : num / Math.pow(10, k * 3);
                        const c = (k >= 1 && n >= 100 ) ? Math.round(n) : n.toFixed(fixed);
                        return (c < 0 ? c : Math.abs(c)) + suffixes[k];
                    }
                }
            })))
    });
}
