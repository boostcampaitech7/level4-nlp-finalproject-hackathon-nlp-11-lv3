import api from './api'

function requestQuery(sessionId, query, company, model, max_tokens, temperature, chatHistory, requestQuerySuccess, requestQueryFail) {
    api
        .post('v1/chatting', {
            session_id: sessionId,
            query: query,
            // llm_model: model,
            max_tokens: max_tokens,
            temperature: temperature,
            company: company,
            chat_history: chatHistory
        })
        .then(requestQuerySuccess)
        .catch(requestQueryFail)
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