import dynamic from 'next/dynamic'

export default dynamic(() => import('./code'), {
    loading: () => <div style={{ color: 'white', padding: '1rem' }}>Loading...</div>,
})
