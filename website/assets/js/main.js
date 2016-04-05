(function() {

    // Elements
    var topnav = document.getElementById('topnav');
    var sidebar = document.getElementById('sidebar');
    
    if(sidebar) {
        var navSelector = 'data-section';
        var sidebarOffset = sidebar.offsetTop;
        var navLinks = document.querySelectorAll('[' + navSelector + ']');
        var elements = getElements();
    }

    var vh = getVh();
    var vhPadding = 525;
    var scrollY = 0;
    var ticking = false;
    var scrollUp = false;

    // Load
    document.addEventListener('DOMContentLoaded', function() {  
        window.addEventListener('scroll', onScroll, false);
        window.addEventListener('resize', onResize, false);
    });


    function onScroll() {
        var newScrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0);
        scrollUp = newScrollY <= scrollY;
        scrollY = newScrollY;

        if(!ticking) {
            requestAnimationFrame(update);
            ticking = true;
        }
    }

    function update() {

        if(sidebar) {
            // Fix sidebar
            if(sidebarOffset - scrollY <= 0) sidebar.classList.add('fixed');
            else sidebar.classList.remove('fixed');

            // Toggle navlinks
            for(var i = 0; i < elements.length; i++) {
                if(inViewport(elements[i])) elements[i].target.classList.add('active');
                else elements[i].target.classList.remove('active');
            }
        }

        // Fix topnav
        if(scrollUp && !(isNaN(scrollY) || scrollY <= vh)) topnav.classList.add('fixed');
        else if(!scrollUp || (isNaN(scrollY) || scrollY <= vh/2)) topnav.classList.remove('fixed');

        ticking = false;
    }

    function onResize() {
        vh = getVh();

        if(sidebar) {
            sidebarOffset = sidebar.offsetTop;
            elements = getElements();
        }
    }

    function getElements() {
        var elements = [];

        for(var i = 0; i < navLinks.length; i++) {
            var trigger = document.getElementById(navLinks[i].getAttribute(navSelector));

            elements.push({
                trigger: trigger,
                target: navLinks[i],
                height: parseInt(trigger.scrollHeight),
                offset: parseInt(trigger.offsetTop)
            });
        }

        return elements;
    }

    function getVh() {
        return Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    }

    function inViewport(element) {
        return (element.offset - scrollY) <= vh/2 && (element.offset - scrollY) > -element.height + vhPadding;
    }
})();
