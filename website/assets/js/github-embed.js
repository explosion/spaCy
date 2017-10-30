'use strict';

import { $$ } from './util.js';

export default class GitHubEmbed {
    /**
     * Embed code from GitHub repositories, similar to Gist embeds. Fetches the
     * raw text and places it inside element.
     * Usage: <pre><code data-gh-embed="spacy/master/examples/x.py"></code><pre>
     * @param {string} user - GitHub user or organization.
     * @param {string} attr - Data attribute used to select containers. Attribute
     *                        value should be path to file relative to user.
     */
    constructor(user, attr) {
        this.url = `https://raw.githubusercontent.com/${user}`;
        this.attr = attr;
        this.error = `\nCan't fetch code example from GitHub :(\n\nPlease use the link below to view the example. If you've come across\na broken link, we always appreciate a pull request to the repository,\nor a report on the issue tracker. Thanks!`;
        [...$$(`[${this.attr}]`)].forEach(el => this.embed(el));
    }

    /**
     * Fetch code from GitHub and insert it as element content. File path is
     * read off the container's data attribute.
     * @param {node} el - The element.
     */
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
