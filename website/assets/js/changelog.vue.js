/**
 * Initialise changelog table for releases and prereleases
 * @param {string} selector - The element selector to initialise the app.
 * @param {string} repo - Repository to load from, in the format user/repo.
 */
export default function(selector, repo) {
    new Vue({
        el: selector,
        data: {
            url: `https://api.github.com/repos/${repo}/releases`,
            releases: [],
            prereleases: [],
            error: false
        },
        beforeMount() {
            fetch(this.url)
                .then(res => res.json())
                .then(json => this.$_update(json))
                .catch(err => { this.error = true });
        },
        updated() {
            window.dispatchEvent(new Event('resize'));  // scroll position for progress
        },
        methods: {
            $_update(json) {
                const allReleases = Object.values(json)
                    .filter(release => release.name)
                    .map(release => ({
                        title: (release.name.split(': ').length == 2) ? release.name.split(': ')[1] : release.name,
                        url: release.html_url,
                        date: release.published_at.split('T')[0],
                        tag: release.tag_name,
                        pre: release.prerelease
                    }));
                this.releases = allReleases.filter(release => !release.pre);
                this.prereleases = allReleases.filter(release => release.pre);
            }
        }
    });
}
