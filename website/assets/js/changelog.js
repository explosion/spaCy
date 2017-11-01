'use strict';

import { Templater, handleResponse } from './util.js';

export default class Changelog {
    /**
     * Fetch and render changelog from GitHub. Clones a template node (table row)
     * to avoid doubling templating markup in JavaScript.
     * @param {string} user - GitHub username.
     * @param {string} repo - Repository to fetch releases from.
     */
    constructor(user, repo) {
        this.url = `https://api.github.com/repos/${user}/${repo}/releases`;
        this.template = new Templater('changelog');
        this.fetchChangelog()
            .then(json => this.render(json))
            .catch(this.showError.bind(this));
        // make sure scroll positions for progress bar etc. are recalculated
        window.dispatchEvent(new Event('resize'));
    }

    fetchChangelog() {
        return new Promise((resolve, reject) =>
            fetch(this.url)
                .then(res => handleResponse(res))
                .then(json => json.ok ? resolve(json) : reject()))
    }

    showError() {
        this.template.get('error').style.display = 'block';
    }

    /**
     * Get template section from template row. Hacky, but does make sense.
     * @param {node} item - Parent element.
     * @param {string} id - ID of child element, set via data-changelog.
     */
    getField(item, id) {
        return item.querySelector(`[data-changelog="${id}"]`);
    }

    render(json) {
        this.template.get('table').style.display = 'block';
        this.row = this.template.get('item');
        this.releases = this.template.get('releases');
        this.prereleases = this.template.get('prereleases');
        Object.values(json)
            .filter(release => release.name)
            .forEach(release => this.renderRelease(release));
        this.row.remove();
    }

    /**
     * Clone the template row and populate with content from API response.
     * https://developer.github.com/v3/repos/releases/#list-releases-for-a-repository
     * @param {string} name - Release title.
     * @param {string} tag (tag_name) - Release tag.
     * @param {string} url (html_url) - URL to the release page on GitHub.
     * @param {string} date (published_at) - Timestamp of release publication.
     * @param {boolean} prerelease - Whether the release is a prerelease.
     */
    renderRelease({ name, tag_name: tag, html_url: url, published_at: date, prerelease }) {
        const container = prerelease ? this.prereleases : this.releases;
        const tagLink = `<a href="${url}" target="_blank"><code>${tag}</code></a>`;
        const title = (name.split(': ').length == 2) ? name.split(': ')[1] : name;
        const row = this.row.cloneNode(true);
        this.getField(row, 'date').textContent = date.split('T')[0];
        this.getField(row, 'tag').innerHTML = tagLink;
        this.getField(row, 'title').textContent = title;
        container.appendChild(row);
    }
}
