import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API_BASE = (() => {
  const base = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
  return base.endsWith('/') ? base.slice(0, -1) : base
})()

function App() {
  const [documents, setDocuments] = useState([])
  const [formValues, setFormValues] = useState({ title: '', content: '' })
  const [editingId, setEditingId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [confirmingDelete, setConfirmingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState(null)

  const documentsEndpoint = `${API_BASE}/documents`

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(documentsEndpoint)
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      const payload = await response.json()
      setDocuments(payload)
    } catch (error) {
      setFeedback({
        type: 'error',
        text:
          error instanceof Error
            ? `Unable to load documents: ${error.message}`
            : 'Unable to load documents.',
      })
    } finally {
      setLoading(false)
    }
  }, [documentsEndpoint])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const updateField = (field) => (event) => {
    setFormValues((current) => ({ ...current, [field]: event.target.value }))
  }

  const resetForm = () => {
    setFormValues({ title: '', content: '' })
    setEditingId(null)
  }

  const handleEdit = (document) => {
    setEditingId(document.id)
    setFormValues({ title: document.title, content: document.content })
    setFeedback(null)
  }

  const handleDeleteRequest = (document) => {
    setConfirmingDelete(document)
    setDeleteError(null)
  }

  const handleDeleteCancel = () => {
    if (deleting) {
      return
    }
    setConfirmingDelete(null)
    setDeleteError(null)
  }

  const handleDeleteConfirm = async () => {
    if (!confirmingDelete) {
      return
    }

    const document = confirmingDelete
    setDeleting(true)
    setDeleteError(null)

    try {
      const response = await fetch(`${documentsEndpoint}/${document.id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(
          detail || `Request failed with status ${response.status}`,
        )
      }

      setDocuments((current) =>
        current.filter((item) => item.id !== document.id),
      )

      if (editingId === document.id) {
        resetForm()
      }

      setDeleteError(null)
      setFeedback({
        type: 'success',
        text: 'Document deleted successfully.',
      })
      setConfirmingDelete(null)
    } catch (error) {
      setDeleteError(
        error instanceof Error
          ? `Unable to delete document: ${error.message}`
          : 'Unable to delete document.',
      )
    } finally {
      setDeleting(false)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setFeedback(null)

    const method = editingId ? 'PUT' : 'POST'
    const endpoint = editingId
      ? `${documentsEndpoint}/${editingId}`
      : `${documentsEndpoint}/`
    const payload = {
      title: formValues.title.trim(),
      content: formValues.content.trim(),
    }

    if (!payload.title || !payload.content) {
      setSaving(false)
      setFeedback({
        type: 'error',
        text: 'Title and content are required.',
      })
      return
    }

    try {
      const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(
          detail || `Request failed with status ${response.status}`,
        )
      }
      const updatedDocument = await response.json()
      if (editingId) {
        setDocuments((current) =>
          current.map((item) =>
            item.id === updatedDocument.id ? updatedDocument : item,
          ),
        )
        setFeedback({ type: 'success', text: 'Document updated successfully.' })
      } else {
        setDocuments((current) => [updatedDocument, ...current])
        setFeedback({ type: 'success', text: 'Document created successfully.' })
      }
      resetForm()
    } catch (error) {
      setFeedback({
        type: 'error',
        text:
          error instanceof Error
            ? `Unable to save document: ${error.message}`
            : 'Unable to save document.',
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="app">
      <div className="app__container">
        <header className="hero">
          <span className="hero__eyebrow">Vector Workspace</span>
          <h1 className="hero__title">Vector Document Manager</h1>
          <p className="hero__subtitle">
            Craft, review, and fine-tune content while embeddings are generated
            automatically in your FastAPI service.
          </p>
        </header>

        <main className="layout">
          <section
            className={`panel panel--form${editingId ? ' panel--active' : ''}`}
          >
            <div className="panel__header">
              <div>
                <h2>{editingId ? 'Edit Document' : 'Create Document'}</h2>
                <p className="panel__hint">
                  {editingId
                    ? 'Update the text below and re-embed instantly.'
                    : 'Add a new document and we will embed it on save.'}
                </p>
              </div>
              {editingId && (
                <span className="panel__badge">Editing ID #{editingId}</span>
              )}
            </div>

            {feedback && (
              <div className={`alert alert--${feedback.type}`}>
                {feedback.text}
              </div>
            )}

            <form className="form" onSubmit={handleSubmit}>
              <label className="form__field">
                <span className="form__label">Title</span>
                <input
                  type="text"
                  value={formValues.title}
                  onChange={updateField('title')}
                  placeholder="Give your document a memorable title"
                  required
                  disabled={saving}
                />
              </label>
              <label className="form__field">
                <span className="form__label">Content</span>
                <textarea
                  value={formValues.content}
                  onChange={updateField('content')}
                  placeholder="Write or paste the content you want to embed"
                  required
                  rows={8}
                  disabled={saving}
                />
              </label>
              <div className="form__actions">
                <button type="submit" disabled={saving}>
                  {saving
                    ? editingId
                      ? 'Updating...'
                      : 'Creating...'
                    : editingId
                      ? 'Update Document'
                      : 'Create Document'}
                </button>
                {editingId && (
                  <button
                    type="button"
                    className="button--ghost"
                    onClick={resetForm}
                    disabled={saving}
                  >
                    Cancel editing
                  </button>
                )}
              </div>
            </form>
          </section>

          <section className="panel panel--list">
            <div className="panel__header">
              <div>
                <h2>Documents</h2>
                <p className="panel__hint">
                  {documents.length > 0
                    ? `Showing ${documents.length} stored ${
                        documents.length === 1 ? 'document' : 'documents'
                      }.`
                    : 'Documents you create will appear here.'}
                </p>
              </div>
              <button
                type="button"
                onClick={loadDocuments}
                disabled={loading || saving || deleting}
                className="button--ghost"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            {loading && <p className="hint">Loading documents...</p>}
            {!loading && documents.length === 0 && (
              <div className="empty">
                <h3>No documents yet</h3>
                <p>
                  Start by creating your first document to generate vector
                  embeddings.
                </p>
              </div>
            )}

            <ul className="document-list">
              {documents.map((document) => {
                const isActive = editingId === document.id
                return (
                  <li
                    key={document.id}
                    className={`document-card${
                      isActive ? ' document-card--active' : ''
                    }`}
                  >
                    <div className="document-card__header">
                      <div>
                        <h3>{document.title}</h3>
                        <span className="document-card__meta">
                          ID #{document.id}
                        </span>
                      </div>
                      <span className="document-card__chip">
                        {document.embedding.length} dims
                      </span>
                    </div>
                    <p className="document-card__content">{document.content}</p>
                    <div className="document-card__footer">
                      <button
                        type="button"
                        className="button--ghost button--small"
                        onClick={() => handleEdit(document)}
                        disabled={saving || deleting}
                      >
                        {isActive ? 'Editing…' : 'Edit document'}
                      </button>
                      <button
                        type="button"
                        className="button--danger button--small"
                        onClick={() => handleDeleteRequest(document)}
                        disabled={saving || deleting}
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                )
              })}
            </ul>
          </section>
        </main>
      </div>

      {confirmingDelete && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          onClick={handleDeleteCancel}
        >
          <div
            className="modal"
            onClick={(event) => event.stopPropagation()}
          >
            <h3 className="modal__title">
              Delete "{confirmingDelete.title}"?
            </h3>
            <p className="modal__body">
              This will permanently remove the document and its embedding from
              the vector store. This action cannot be undone.
            </p>
            {deleteError && <p className="modal__error">{deleteError}</p>}
            <div className="modal__actions">
              <button
                type="button"
                className="button--danger"
                onClick={handleDeleteConfirm}
                disabled={deleting}
              >
                {deleting ? 'Deleting…' : 'Delete document'}
              </button>
              <button
                type="button"
                className="button--ghost"
                onClick={handleDeleteCancel}
                disabled={deleting}
              >
                Keep document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
