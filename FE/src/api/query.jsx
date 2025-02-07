import api from './api'

function requestQuery(query, max_tokens, temperature, requestQuerySuccess, requestQueryFail) {
    api
        .post('v1/query/', {
            query: query,
            max_tokens: max_tokens,
            temperature: temperature,
        })
        .then(requestQuerySuccess)
        .catch(requestQueryFail);
}

function uploadFile(file, uploadFileSuccess, uploadFileFail) {
    api
        .post('v1/documents/upload/', {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            file: file
        })
        .then(uploadFileSuccess)
        .catch(uploadFileFail)
}

export { requestQuery, uploadFile };