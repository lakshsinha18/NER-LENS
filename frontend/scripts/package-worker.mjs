import { cpSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const root = process.cwd()
const destination = resolve(root, 'dist/server')
mkdirSync(destination, { recursive: true })
cpSync(resolve(root, 'worker/index.js'), resolve(destination, 'index.js'))
