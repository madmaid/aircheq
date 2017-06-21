import * as React from "react"
import styled from "styled-components"
import * as ReactModal from 'react-modal'

const Modal = (props: any ) => {
        const style = {
            overlay: {
                backgroundColor: "rgba(0, 0, 0, 0.75)",
            }
        }
        return <ReactModal {...props} style={style} />
}
const OpenButton = styled.button`
`
const CloseButton= styled.button`
    position: absolute;
    right: 20px;
    bottom: 20px;
`

export {
    Modal,
    OpenButton,
    CloseButton,
}