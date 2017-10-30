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
            .then(({ text, ok }) => ok ? this.render(el, text) : false)
        el.parentElement.removeAttribute('data-loading');
    }

    /**
     * Add text to container and apply syntax highlighting via Prism, if available.
     * @param {node} el - The element.
     * @param {string} text - The raw code, fetched from GitHub.
     */
    render(el, text) {
        el.textContent = text;
        if (window.Prism) Prism.highlightElement(el);
    }
}
