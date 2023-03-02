#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

from django import template

from base.templatetags.conjoin import conjoin

register = template.Library()

# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/#simple-tags


@register.simple_tag
def delete_modal_ids(entity: str) -> dict:
    """
    Generate the ids for the elements of the delete entity modal
    :param entity: entity name
    :return: tag ids
    """
    entity_conjoin = conjoin(entity)

    confirm_id = f'id__{entity_conjoin}-delete-confirm-modal'
    deleted_id = f'id__{entity_conjoin}-deleted-modal'

    return {
        # id of the delete confirmation modal
        'confirm_id': confirm_id,
        # id of the label of the delete confirmation modal
        'confirm_id_label': f'{confirm_id}-label',
        # id of the deleted modal
        'deleted_id': deleted_id,
        # id of the label of the deleted modal
        'deleted_id_label': f'{deleted_id}-label',
        # id of the body of the deleted modal
        'deleted_id_body': f'{deleted_id}-body',
        # id of delete button of the delete confirmation modal
        'delete_btn_id': f'id__btn-{entity_conjoin}-delete-confirm',
        # id of cancel button of the delete confirmation modal
        'cancel_btn_id': f'id__btn-{entity_conjoin}-delete-cancel',
        # id of close button of the delete confirmation modal
        'close_btn_id': f'id__btn-{entity_conjoin}-delete-close',
        # id of var to hold the entity delete url
        'url_var_id': f'id__{entity_conjoin}-delete-url',
        'entity_conjoin': entity_conjoin,
    }
