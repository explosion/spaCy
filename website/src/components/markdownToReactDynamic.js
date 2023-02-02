import dynamic from 'next/dynamic'

export default dynamic(() => import('./markdownToReact'), {
    loading: () => <p>Loading...</p>,
})
