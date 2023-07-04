import sidebars from './sidebars.json'

export const sidebarUsageFlat = sidebars
    .find((sidebar) => sidebar.section === 'usage')
    .items.flatMap((item) => item.items)
