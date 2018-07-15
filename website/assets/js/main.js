/**
 * Initialise changelog
 */
import initChangelog from './changelog.vue.js';

{
    const selector = '[data-vue="changelog"]';
    if (window.Vue && document.querySelector(selector)) {
        initChangelog(selector, 'explosion/spacy');
    }
}

/**
 * Initialise models
 */
import initModels from './models.vue.js';

{
    if (window.Vue && document.querySelector('[data-model]')) {
        initModels('explosion/spacy-models')
    }
}

/**
 * Initialise Universe
 */
import initUniverse from './universe.vue.js';

{
    const selector = '[data-vue="universe"]';
    if (window.Vue && document.querySelector(selector)) {
        initUniverse(selector, '/universe/universe.json');
    }
}

/**
 * Initialise Quickstart
 */
{
    if (document.querySelector('#qs') && window.Quickstart) {
        new Quickstart('#qs');
    }
}

/**
 * Initialise Juniper
 */
{
    if (window.Juniper) {
        new Juniper({
            repo: 'ines/spacy-io-binder',
            storageExpire: 60
        });
    }
}

/**
 * Highlight section in viewport in sidebar, using in-view library
 */
{
    const sectionAttr = 'data-section';
    const navAttr = 'data-nav';
    const activeClass = 'is-active';
    const sidebarAttr = 'data-sidebar-active';
    const sections = [...document.querySelectorAll(`[${navAttr}]`)];
    const currentItem = document.querySelector(`[${sidebarAttr}]`);
    if (window.inView) {
        if (currentItem && Element.prototype.scrollIntoView && !inView.is(currentItem)) {
            currentItem.scrollIntoView();
        }
        if (sections.length) {  // highlight first item regardless
            sections[0].classList.add(activeClass);
        }
        inView(`[${sectionAttr}]`).on('enter', section => {
            const id = section.getAttribute(sectionAttr);
            const el = document.querySelector(`[${navAttr}="${id}"]`);
            if (el) {
                sections.forEach(el => el.classList.remove(activeClass));
                el.classList.add(activeClass);
                if (Element.prototype.scrollIntoView && !inView.is(el)) {
                    el.scrollIntoView();
                }
            }
        });
    }
}

/**
 * Simple, collapsible accordion sections.
 * Inspired by: https://inclusive-components.design/collapsible-sections/
 */
{
    const elements = [...document.querySelectorAll('.js-accordion')];
    elements.forEach(el => el.addEventListener('click', ({ target }) => {
        const exp = target.getAttribute('aria-expanded') === 'true' || false;
        target.setAttribute('aria-expanded', !exp);
        target.parentElement.nextElementSibling.hidden = exp;
    }));
}

/**
 * Reading indicator as progress bar
 * @param {string} selector - Selector of <progress> element.
 */
class ProgressBar {
    constructor(selector) {
        this.scrollY = 0;
        this.sizes = this.updateSizes();
        this.el = document.querySelector(selector);
        this.el.setAttribute('max', 100);
        window.addEventListener('scroll', ev => {
            this.scrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0);
            requestAnimationFrame(this.update.bind(this));
        });
        window.addEventListener('resize', ev => {
            this.sizes = this.updateSizes();
            requestAnimationFrame(this.update.bind(this));
        });
    }

    update() {
        const offset = 100 - ((this.sizes.height - this.scrollY - this.sizes.vh) / this.sizes.height * 100);
        this.el.setAttribute('value', (this.scrollY == 0) ? 0 : offset || 0);
    }

    updateSizes() {
        return {
            height: Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight),
            vh: Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
        }
    }
}

new ProgressBar('.js-progress');

/**
 * Embed code from GitHub repositories, similar to Gist embeds. Fetches the
 * raw text and places it inside element.
 * Usage: <pre><code data-gh-embed="spacy/master/examples/x.py"></code><pre>
 */
{
    const attr = 'data-gh-embed';
    const url = 'https://raw.githubusercontent.com/explosion';
    const elements = [...document.querySelectorAll(`[${attr}]`)];
    elements.forEach(el => {
        el.parentElement.setAttribute('data-loading', '');
        fetch(`${url}/${el.getAttribute(attr)}`)
            .then(res => res.text().then(text => ({ text, ok: res.ok })))
            .then(({ text, ok }) => {
                if (ok) {
                    el.textContent = text;
                    if (window.Prism) Prism.highlightElement(el);
                }
                el.parentElement.removeAttribute('data-loading');
            })
    });
}
