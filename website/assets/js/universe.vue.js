export default function(selector, dataPath) {
    Vue.use(VueMarkdown);

    new Vue({
        el: selector,
        data: {
            filteredResources: [],
            allResources: [],
            projectCats: {},
            educationCats: {},
            filterVals: ['category'],
            activeMenu: 'all',
            selected: null,
            loading: false
        },
        computed: {
            resources() {
                return this.filteredResources.sort((a, b) => a.id.localeCompare(b.id));
            },
            categories() {
                return Object.assign({}, this.projectCats, this.educationCats);
            }
        },

        beforeMount() {
            this.loading = true;
            window.addEventListener('popstate', this.$_init);
            fetch(dataPath)
                .then(res => res.json())
                .then(({ resources, projectCats, educationCats }) => {
                    this.allResources = resources || [];
                    this.filteredResources = resources || [];
                    this.projectCats = projectCats || {};
                    this.educationCats = educationCats || {};
                    this.$_init();
                    this.loading = false;
                });
        },
        updated() {
            if (window.Prism) Prism.highlightAll();
            // make sure scroll positions for progress bar etc. are recalculated
            window.dispatchEvent(new Event('resize'));
        },
        methods: {
            getAuthorLink(id, link) {
                if (id == 'twitter') return `https://twitter.com/${link}`;
                else if (id == 'github') return `https://github.com/${link}`;
                return link;
            },

            filterBy(id, selector = 'category') {
                window.scrollTo(0, 0);
                if (!this.filterVals.includes(selector)) {
                    return;
                }
                const resources = this.$_filterResources(id, selector);
                if (!resources.length) return;
                this.selected = null;
                this.activeMenu = id;
                this.filteredResources = resources;
            },

            viewResource(id) {
                const res = this.allResources.find(r => r.id == id);
                if (!res) return;
                this.selected = res;
                this.activeMenu = null;
                if (this.$_getQueryVar('id') != res.id) {
                    this.$_updateUrl({ id: res.id });
                }
                window.scrollTo(0, 0);
            },

            $_filterResources(id, selector) {
                if (id == 'all') {
                    if (window.location.search != '') {
                        this.$_updateUrl({});
                    }
                    return this.allResources;
                }
                const resources = this.allResources
                    .filter(res => (res[selector] || []).includes(id));
                if (resources.length && this.$_getQueryVar(selector) != id) {
                    this.$_updateUrl({ [selector]: id });
                }
                return resources;
            },

            $_init() {
                const current = this.$_getQueryVar('id');
                if (current) {
                    this.viewResource(current);
                    return;
                }
                for (let filterVal of this.filterVals) {
                    const queryVar = this.$_getQueryVar(filterVal);
                    if (queryVar) {
                        this.filterBy(queryVar, filterVal);
                        return;
                    }
                }
                this.filterBy('all');
            },

            $_getQueryVar(key) {
                const query = window.location.search.substring(1);
                const params = query.split('&').map(param => param.split('='));
                for(let param of params) {
                    if (param[0] == key) {
                        return decodeURIComponent(param[1]);
                    }
                }
                return false;
            },

            $_updateUrl(params) {
                const loc = Object.keys(params)
                    .map(param => `${param}=${encodeURIComponent(params[param])}`);
                const url = loc.length ? '?' + loc.join('&')
                    : window.location.origin + window.location.pathname;
                window.history.pushState(params, null, url);
            }
        }
    })
}
