'use strict';

export const $ = document.querySelector.bind(document);
export const $$ = document.querySelectorAll.bind(document);

export class Templater {
    /**
     * Mini templating engine based on data attributes. Selects elements based
     * on a data-tpl and data-tpl-key attribute and can set textContent
     * and innterHtml.
     * @param {string} templateId - Template section, e.g. value of data-tpl.
     */
    constructor(templateId) {
        this.templateId = templateId;
    }

    /**
     * Get an element from the template and return it.
     * @param {string} key - Name of the key within the current template.
     */
    get(key) {
        return $(`[data-tpl="${this.templateId}"][data-tpl-key="${key}"]`);
    }

    /**
     * Fill the content of a template element with a value.
     * @param {string} key - Name of the key within the current template.
     * @param {string} value - Content to insert into template element.
     * @param {boolean} html - Insert content as HTML. Defaults to false.
     */
    fill(key, value, html = false) {
        const el = this.get(key);
        if (html) el.innerHTML = value || '';
        else el.textContent = value || '';
        return el;
    }
}

/**
 * Handle API response and assign status to returned JSON.
 * @param {Response} res – The response.
 */
export const handleResponse = res => {
    if (res.ok) return res.json()
        .then(json => Object.assign({}, json, { ok: res.ok }))
    else return ({ ok: res.ok })
};

/**
 * Convert a number to a string and add thousand separator.
 * @param {number|string} num - The number to convert.
 * @param {string} separator – Thousand separator.
 */
export const convertNumber = (num = 0, separator = ',') =>
    num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator);

/**
 * Abbreviate a number, e.g. 14249930 --> 14.25m.
 * @param {number|string} num - The number to convert.
 * @param {number} fixed - Number of decimals.
 */
export const abbrNumber = (num = 0, fixed = 1) => {
    const suffixes = ['', 'k', 'm', 'b', 't'];
    if (num === null || num === 0) return 0;
    const b = num.toPrecision(2).split('e');
    const k = (b.length === 1) ? 0 : Math.floor(Math.min(b[1].slice(1), 14) / 3);
    const n = (k < 1) ? num : num / Math.pow(10, k * 3);
    const c = (k >= 1 && n >= 100 ) ? Math.round(n) : n.toFixed(fixed);
    return (c < 0 ? c : Math.abs(c)) + suffixes[k];
}
