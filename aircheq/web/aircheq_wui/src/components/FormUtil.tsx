import styled from "styled-components"

const InputForm = styled.form`
    display: flex;
`
const Input = styled.input`
    flex: 1;
    min-width: 20px;
`
const SendButton = styled.button`
    min-width: 10px;
`

export {
    Input,
    InputForm,
    SendButton
}