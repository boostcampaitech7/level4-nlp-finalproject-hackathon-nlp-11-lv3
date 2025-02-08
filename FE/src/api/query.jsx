import api from './api'

function requestQuery(query, model, max_tokens, temperature, requestQuerySuccess, requestQueryFail) {
    api
        .post('v1/query/', {
            query: query,
            llm_model: model,
            max_tokens: max_tokens,
            temperature: temperature,
        })
        .then(requestQuerySuccess)
        .catch(requestQueryFail);
}

function uploadFile(file, uploadFileSuccess, uploadFileFail) {
    api
        .post('v1/documents/upload', 
            file, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            },
        )
        .then(uploadFileSuccess)
        .catch(uploadFileFail)
}

export { requestQuery, uploadFile };