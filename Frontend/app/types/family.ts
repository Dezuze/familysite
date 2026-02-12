export interface FamilyMember {
  id: number
  name: string // Full name property
  first_name?: string
  last_name?: string
  photo?: string // from FamilyTreeView
  profile_pic?: string // from FamilyMemberSerializer
  age?: number
  gender?: string
  date_of_birth?: string
  relation?: string // from FamilyTreeView (role)
  children?: FamilyMember[]
  parents?: number[] | any[]
  role?: string
  
  // Details
  email_id?: string
  phone_no?: string
  address?: string
  bio?: string
  occupation?: string
  education?: string
  blood_group?: string
  place_of_work?: string
  spouse?: any // ID or name depending on view
  
  // New fields
  is_deceased?: boolean
  is_committee?: boolean
  date_of_death?: string
  crematory?: string
  parent?: any // FK object or ID
  username?: string // for tree focus
}
