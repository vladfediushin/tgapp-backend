import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method === 'POST') {
    const { message } = req.body
    console.log('[FRONT LOG]', message)
    return res.status(200).json({ status: 'ok' })
  }

  res.status(405).json({ error: 'Method Not Allowed' })
}
