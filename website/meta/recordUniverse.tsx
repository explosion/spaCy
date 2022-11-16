import universe from './universe.json'

export const recordUniverseCategories = Object.fromEntries(
    universe.categories.flatMap((category) => category.items.map((item) => [item.id, item]))
)
