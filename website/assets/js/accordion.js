'use strict';

import { $$ } from './util.js';

export default class Accordion {
    /**
     * Simple, collapsible accordion sections.
     * Inspired by: https://inclusive-components.design/collapsible-sections/
     * @param {string} selector - Query selector of button element.
     */
    constructor(selector) {
        [...$$(selector)].forEach(btn =>
            btn.addEventListener('click', this.onClick.bind(this)))
    }

    /**
     * Toggle aria-expanded attribute on button and visibility of section.
     * @param {node} Event.target - The accordion button.
     */
    onClick({ target }) {
        const exp = target.getAttribute('aria-expanded') === 'true' || false;
        target.setAttribute('aria-expanded', !exp);
        target.parentElement.nextElementSibling.hidden = exp;
    }
}
