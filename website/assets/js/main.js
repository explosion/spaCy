//- ----------------------------------
//- 💫 MAIN JAVASCRIPT
//- ----------------------------------

'use strict';

const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);

{
    const updateVh = () => Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    const nav = $('.js-nav');
    const sidebar = $('.js-sidebar');
    const vhPadding = 525;

    let vh = updateVh();
    let scrollY = 0;
    let scrollUp = false;

    const updateNav = () => {
        const vh = updateVh();
        const newScrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0);
        scrollUp = newScrollY <= scrollY;
        scrollY = newScrollY;

        if(scrollUp && !(isNaN(scrollY) || scrollY <= vh)) nav.classList.add('is-fixed');
        else if(!scrollUp || (isNaN(scrollY) || scrollY <= vh/2)) nav.classList.remove('is-fixed');
    }

    const updateSidebar = () => {
        const sidebar = $('.js-sidebar');
        if(sidebar.offsetTop - scrollY <= 0) sidebar.classList.add('is-fixed');
        else sidebar.classList.remove('is-fixed');

        [...$$('[data-section]')].map(el => {
            const trigger = el.getAttribute('data-section');

            if(trigger) {
                const target = $(`#${trigger}`);
                const offset = parseInt(target.offsetTop);
                const height = parseInt(target.scrollHeight);

                if((offset - scrollY) <= vh/2 && (offset - scrollY) > -height + vhPadding) {
                    [...$$('[data-section]')].forEach(item => item.classList.remove('is-active'));
                    $(`[data-section="${trigger}"]`).classList.add('is-active');
                }
            }
        });
    }

    window.addEventListener('resize', () => vh = updateVh());
    window.addEventListener('scroll', updateNav);
    if($('.js-sidebar')) window.addEventListener('scroll', updateSidebar);
}
