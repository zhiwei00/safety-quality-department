import SparkMD5 from 'spark-md5'
import {createRequest, default as request, sendFormRequest} from '../utils/request'

/**
 * 自定义的chunkUpload处理器
 */
export default class DfsChunkUploadHandler {
  /**
   * Constructor
   *
   * @param {File} file
   * @param {Object} options
   */
  constructor(file, options) {
    this.file = file
    this.options = options
  }

  /**
   * Gets the max retries from options
   */
  get maxRetries() {
    return parseInt(this.options.maxRetries)
  }

  /**
   * Gets the max number of active chunks being uploaded at once from options
   */
  get maxActiveChunks() {
    return parseInt(this.options.maxActive)
  }

  /**
   * Gets the file type
   */
  get fileType() {
    return this.file.type
  }

  /**
   * Gets the file size
   */
  get fileSize() {
    return this.file.size
  }

  /**
   * Gets the file name
   */
  get fileName() {
    return this.file.name
  }

  /**
   * Gets the file status
   */
  get fileUploadStatus() {
    return this.file.status
  }

  /**
   * get the file md5
   */
  get symbolicLinkId() {
    return this.file.symbolicLinkId
  }

  /**
   * get the file md5
   */
  get fileId() {
    return this.file.fileId
  }

  /**
   * get the file md5
   */
  get uuid() {
    return this.file.uuid
  }

  /**
   * get the file md5
   */
  get md5() {
    return this.file.md5
  }

  /**
   * Gets action (url) to upload the file
   */
  get action() {
    return this.options.action || null
  }

  /**
   * Gets action (url) to upload the file
   */
  get chunkEndAction() {
    return this.options.chunkEndAction || null
  }

  get startBody() {
    return {
      ...this.file.startBody,
      ...this.file.data,
      mimeType: this.fileType,
      fileSize: this.fileSize,
      fileName: this.fileName,
      md5: this.md5,
      chunkCount: this.chunks.length
    }
  }

  get uploadBody() {
    return {
      ...this.file.uploadBody,
      ...this.file.data,
      fileId: this.fileId,
      chunkCount: this.chunks.length
    }
  }

  get finishBody() {
    return {
      ...this.file.finishBody,
      ...this.file.data,
      fileId: this.fileId,
      fileName: this.fileName,
      chunkCount: this.chunks.length
    }
  }

  get finallyBody() {
    return {
      ...this.file.finishBody,
      ...this.file.data,
      symbolicLinkId: this.symbolicLinkId,
      uuid: this.uuid,
      fileSize: this.fileSize,
      fileName: this.fileName,
      md5: this.md5
    }
  }

  /**
   * Gets the headers of the requests from options
   */
  get headers() {
    return this.options.headers || {}
  }

  /**
   * Whether it's ready to upload files or not
   */
  get readyToUpload() {
    return !!this.chunks
  }

  /**
   * Gets the progress of the chunk upload
   * - Gets all the completed chunks
   * - Gets the progress of all the chunks that are being uploaded
   */
  get progress() {
    const completedProgress = (this.chunksUploaded.length / this.chunks.length) * 100
    const uploadingProgress = this.chunksUploading.reduce((progress, chunk) => {
      return progress + ((chunk.progress | 0) / this.chunks.length)
    }, 0)

    return Number(Math.min(completedProgress + uploadingProgress, 100).toFixed(2))
  }

  /**
   * Gets all the chunks that are pending to be uploaded
   */
  get chunksToUpload() {
    return this.chunks.filter(chunk => {
      return !chunk.active && !chunk.uploaded
    })
  }

  /**
   * Whether there are chunks to upload or not
   */
  get hasChunksToUpload() {
    return this.chunksToUpload.length > 0
  }

  /**
   * Gets all the chunks that are uploading
   */
  get chunksUploading() {
    return this.chunks.filter(chunk => {
      return !!chunk.xhr && !!chunk.active
    })
  }

  /**
   * Gets all the chunks that have finished uploading
   */
  get chunksUploaded() {
    return this.chunks.filter(chunk => {
      return !!chunk.uploaded
    })
  }

  get chunkSize() {
    return 4 * 1024 * 1024
  }

  /**
   * Creates all the chunks in the initial state
   */
  createChunks() {
    this.chunks = []

    let start = 0
    let end = this.chunkSize
    // chunk序号
    let index = 0
    while (start < this.fileSize) {
      let chunk = {
        blob: this.file.file.slice(start, end),
        startOffset: start,
        active: false,
        retries: this.maxRetries,
        index: index
      }
      this.chunks.push(chunk)
      start = end
      end = start + this.chunkSize
      index++
    }
  }

  /**
   * 计算MD5
   */
  computerMd5() {
    console.log('computer md5')
    return new Promise((resolve, reject) => {
      const spark = new SparkMD5.ArrayBuffer()
      const fileReader = new FileReader()
      let currentChunk = 0
      const chunkCount = this.chunks.length
      this.file.checkMd5 = true

      fileReader.onload = e => {
        this.chunks[currentChunk].md5 = SparkMD5.ArrayBuffer.hash(e.target.result)
        spark.append(e.target.result)
        currentChunk += 1
        if (currentChunk < this.chunks.length) {
          loadNext()
        } else {
          this.file.checkMd5 = false
          return resolve(spark.end())
        }
      }

      fileReader.onerror = e => reject(e)

      let loadNext = () => {
        this.file.progress = ((currentChunk / chunkCount) * 100).toFixed(2)
        fileReader.readAsArrayBuffer(this.chunks[currentChunk].blob)
      }

      loadNext()
    })
  }

  /**
   * 过滤已上传过的 chunks
   */
  filterChunks() {
    if (this.indexList !== null && this.indexList !== undefined) {
      this.chunks.forEach((chunk, index) => {
        if (this.indexList.indexOf(index) > -1) {
          chunk.uploaded = true
        }
      })
    }
  }

  refreshChunksUploaded() {
    this.chunks.forEach((chunk, index) => {
      chunk.uploaded = true
    })
  }

  /**
   * Updates the progress of the file with the handler's progress
   */
  updateFileProgress() {
    // this.file.uploader.update(this.file, { progress: this.progress })
    this.file.progress = this.progress
    this.file.uploader.refreshProgress()
  }

  /**
   * Paues the upload process
   * - Stops all active requests
   * - Sets the file not active
   */
  pause() {
    this.file.active = false
    this.stopChunks()
  }

  /**
   * Stops all the current chunks
   */
  stopChunks() {
    this.chunksUploading.forEach(chunk => {
      chunk.xhr.abort()
      chunk.active = false
    })
  }

  /**
   * Resumes the file upload
   * - Sets the file active
   * - Starts the following chunks
   */
  resume() {
    this.file.active = true
    this.startUploadChunk()
  }

  /**
   * Starts the file upload
   *
   * @returns Promise
   * - resolve  The file was uploaded
   * - reject   The file upload failed
   */
  upload() {
    this.promise = new Promise((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
    this.start()

    return this.promise
  }

  /**
   * Start phase
   * Sends a request to the backend to initialise the chunks
   */
  start() {
    this.createChunks()
    this.computerMd5().then(md5 => {
      this.file.md5 = md5
      request({
        method: 'POST',
        headers: Object.assign({}, this.headers, {
          'Content-Type': 'application/json'
        }),
        url: this.action + '/start',
        body: Object.assign(this.startBody, {})
      }).then(res => {
        if (res.code !== 0) {
          this.file.response = res
          return this.reject('server')
        }

        this.file.status = res.result.status
        this.file.symbolicLinkId = res.result.data.symbolicLinkId
        this.file.uuid = res.result.data.uuid
        this.file.fileId = res.result.data.fileId

        // 返回success直接执行finally
        if (this.file.status === 'success') {
          this.refreshChunksUploaded()
          this.finally()
          this.resolve(res)
        } else {
          // 判断已上传
          this.indexList = res.result.data.indexList
          this.filterChunks()
          this.startUploadChunk()
        }
      }).catch(res => {
        this.file.response = res
        this.reject('server')
      })
    }).catch(e => {
      throw new Error('md5')
    })
  }

  /**
   * Starts to upload chunks
   */
  startUploadChunk() {
    for (let i = 0; i < this.maxActiveChunks; i++) {
      this.uploadNextChunk()
    }
  }

  /**
   * Uploads the next chunk
   * - Won't do anything if the process is paused
   * - Will start finish phase if there are no more chunks to upload
   */
  uploadNextChunk() {
    if (this.file.active) {
      if (this.hasChunksToUpload) {
        return this.uploadChunk(this.chunksToUpload[0])
      }

      if (this.chunksUploading.length === 0) {
        return this.finish()
      }
    }
  }

  /**
   * Uploads a chunk
   * - Sends the chunk to the backend
   * - Sets the chunk as uploaded if everything went well
   * - Decreases the number of retries if anything went wrong
   * - Fails if there are no more retries
   *
   * @param {Object} chunk
   */
  uploadChunk(chunk) {
    chunk.progress = 0
    chunk.active = true
    this.updateFileProgress()
    chunk.xhr = createRequest({
      method: 'POST',
      headers: this.headers,
      url: this.action + '/upload'
    })

    chunk.xhr.upload.addEventListener('progress', function (evt) {
      if (evt.lengthComputable) {
        chunk.progress = Math.round(evt.loaded / evt.total * 100)
      }
    }, false)

    sendFormRequest(chunk.xhr, Object.assign(this.uploadBody, {
      index: chunk.index,
      chunk: chunk.blob,
      md5: chunk.md5
    })).then(res => {
      chunk.active = false
      if (res.code === 0 && res.result.status === 'success') {
        chunk.uploaded = true
      } else {
        if (chunk.retries-- <= 0) {
          this.stopChunks()
          return this.reject('upload')
        }
      }

      this.uploadNextChunk()
    }).catch(() => {
      chunk.active = false
      if (chunk.retries-- <= 0) {
        this.stopChunks()
        return this.reject('upload')
      }

      this.uploadNextChunk()
    })
  }

  /**
   * Finish phase
   * Sends a request to the backend to finish the process
   */
  finish() {
    this.updateFileProgress()
    this.finally()

    request({
      method: 'POST',
      headers: Object.assign({}, this.headers, {
        'Content-Type': 'application/json'
      }),
      url: this.action + '/finish',
      body: Object.assign(this.finishBody, {})
    }).then(res => {
      this.file.response = res
      if (res.code !== 0 || res.result.status !== 'success') {
        return this.reject('server')
      }

      this.resolve(res)
    }).catch(res => {
      this.file.response = res
      this.reject('server')
    })
  }

  finally() {
    this.file.progress = 100
    this.file.uploader.refreshProgress()

    request({
      method: 'POST',
      headers: Object.assign({}, this.headers, {
        'Content-Type': 'application/json'
      }),
      url: this.chunkEndAction,
      body: Object.assign(this.finallyBody, {})
    }).then(res => {
      // do nothing
    }).catch(res => {
      // do nothing
    })
  }
}
