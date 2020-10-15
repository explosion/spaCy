import React, { useState, useEffect, useRef } from 'react'
import { document, window } from 'browser-monads'

import classes from '../styles/progress.module.sass'

function getOffset() {
    const height = Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
    )
    const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
    return { height, vh }
}

function getScrollY() {
    const pos = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0)
    return isNaN(pos) ? 0 : pos
}

export default function Progress() {
    const progressRef = useRef()
    const [initialized, setInitialized] = useState(false)
    const [offset, setOffset] = useState(getOffset())
    const [scrollY, setScrollY] = useState(getScrollY())

    function handleScroll() {
        setScrollY(getScrollY())
    }

    function handleResize() {
        setOffset(getOffset())
    }

    useEffect(() => {
        if (!initialized && progressRef.current) {
            handleResize()
            setInitialized(true)
        }
        window.addEventListener('scroll', handleScroll)
        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('scroll', handleScroll)
            window.removeEventListener('resize', handleResize)
        }
    }, [initialized, progressRef])

    const { height, vh } = offset
    const total = 100 - ((height - scrollY - vh) / height) * 100
    const value = scrollY === 0 ? 0 : total || 0
    return <progress ref={progressRef} className={classes.root} value={value} max="100" />
}
