import React from 'react'

import Grid from '../components/grid'
import { Label } from '../components/typography'
import Link from '../components/link'

import Logo from '-!svg-react-loader!../images/logo.svg'
import patternBlue from '../images/pattern_blue.jpg'
import patternGreen from '../images/pattern_green.jpg'
import patternPurple from '../images/pattern_purple.jpg'

const colors = {
    dark: 'var(--color-front)',
    medium: 'var(--color-dark)',
    light: 'var(--color-subtle)',
    faint: 'var(--color-subtle-light)',
    blue: 'var(--color-theme-blue)',
    'dark blue': 'var(--color-theme-blue-dark)',
    green: 'var(--color-theme-green)',
    'dark green': 'var(--color-theme-green-dark)',
    purple: 'var(--color-theme-purple)',
    'dark purple': 'var(--color-theme-purple-dark)',
    red: 'var(--color-red-medium)',
    'light red': 'var(--color-red-light)',
    yellow: 'var(--color-yellow-medium)',
    'light yellow': 'var(--color-yellow-light)',
}

const patterns = {
    'blue pattern': patternBlue,
    'green pattern': patternGreen,
    'purple pattern': patternPurple,
}

const Card = ({ style = {}, children }) => (
    <div
        style={{
            borderRadius: 'var(--border-radius)',
            boxShadow: 'var(--box-shadow)',
            marginBottom: 'var(--spacing-sm)',
        }}
    >
        <div
            style={{
                borderTopLeftRadius: 'var(--border-radius)',
                borderTopRightRadius: 'var(--border-radius)',
                ...style,
            }}
        />
        <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>{children}</div>
    </div>
)

export const Colors = () => (
    <Grid cols={4} narrow>
        {Object.keys(colors).map(name => (
            <Card key={name} style={{ height: 80, background: colors[name] }}>
                <Label>{name}</Label>
            </Card>
        ))}
    </Grid>
)

export const Patterns = () => {
    const imgStyle = name => ({
        height: 125,
        background: `url(${patterns[name]}) center/150% repeat`,
    })
    const textStyle = { fontSize: 'var(--font-size-xs)', color: 'var(--color-subtle-dark)' }
    const linkStyle = { color: 'var(--color-dark)' }
    return (
        <Grid cols={3} narrow>
            {Object.keys(patterns).map(name => (
                <Card key={name} style={imgStyle(name)}>
                    <Label>{name}</Label>
                    <span style={textStyle}>
                        by
                        <Link to="https://dribbble.com/kemal" hidden style={linkStyle} ws>
                            Kemal Şanlı
                        </Link>
                    </span>
                </Card>
            ))}
        </Grid>
    )
}

export const Logos = () => {
    const style = {
        padding: '0 3rem',
        border: '1px solid var(--color-subtle)',
        borderRadius: 'var(--border-radius)',
        boxShadow: 'var(--box-shadow)',
    }
    return (
        <Grid cols={2} narrow>
            <div style={style}>
                <Logo />
            </div>
            <div
                style={{
                    ...style,
                    background: 'var(--color-theme-blue)',
                    borderColor: 'var(--color-theme-blue)',
                }}
            >
                <Logo style={{ color: 'var(--color-back)' }} />
            </div>
        </Grid>
    )
}
