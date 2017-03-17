//- ----------------------------------
//- 💫 MAIN JAVASCRIPT
//- ----------------------------------

'use strict'

{
    const nav = document.querySelector('.js-nav')
    const fixedClass = 'is-fixed'
    let vh, scrollY = 0, scrollUp = false

    const updateVh = () => Math.max(document.documentElement.clientHeight, window.innerHeight || 0)

    const updateNav = () => {
        const vh = updateVh()
        const newScrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0)
        if (newScrollY != scrollY) scrollUp = newScrollY <= scrollY
        scrollY = newScrollY

        if(scrollUp && !(isNaN(scrollY) || scrollY <= vh)) nav.classList.add(fixedClass)
        else if (!scrollUp || (isNaN(scrollY) || scrollY <= vh/2)) nav.classList.remove(fixedClass)
    }

    window.addEventListener('scroll', () => requestAnimationFrame(updateNav))
}
